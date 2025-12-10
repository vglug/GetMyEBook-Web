from flask import redirect, url_for, flash, Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from slugify import slugify
from .forms import ThreadCreationForm
from cps.forum.database.models import Thread, Category
from cps.forum.src.decorators.email_verified import email_verified
from sqlalchemy.orm import joinedload

thread_blueprint = Blueprint("threads", __name__, template_folder="templates")




@thread_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.role_admin():
        flash("Only administrators can create new threads.", "danger")
        return redirect(url_for("main.index"))

    thread_form = ThreadCreationForm()

    # Pre-fill from query args if not submitted
    if request.method == 'GET':
        title_arg = request.args.get('title')
        if title_arg and not thread_form.title.data:
            thread_form.title.data = title_arg
            thread_form.content.data = f"Official discussion thread for **{title_arg}**."

    if thread_form.validate_on_submit():
        title = thread_form.title.data
        category_id = thread_form.category_id.data
        content = thread_form.content.data
        user_id = current_user.id

        thread = Thread(title=title,
                        category_id=category_id,
                        content=content,
                        user_id=user_id,
                        slug=slugify(title),
                        views_count=0
                        )
        thread.save()

        flash("Your question has been posted successfully", "success")
        return redirect(url_for("main.index"))

    return render_template("threads/create.html", form=thread_form)


@thread_blueprint.route("/book/<int:book_id>")
@login_required
def book_thread(book_id):
    from cps import calibre_db
    book = calibre_db.get_book(book_id)
    if not book:
        abort(404)
    
    # Find thread by title matching book title
    thread = Thread.query.filter_by(title=book.title).first()
    
    if thread:
        return redirect(url_for('threads.show', 
                              category_slug=thread.category.slug, 
                              thread_slug=thread.slug))
    
    # If no thread found
    if current_user.role_admin():
        flash(f"No discussion thread found for '{book.title}'. You can create one now.", "info")
        return redirect(url_for('threads.create', title=book.title))
    else:
        flash(f"No discussion thread has been created for '{book.title}' yet.", "info")
        # Go to forum index or search?
        # Search might show partial matches
        # Assuming main.index is the forum home
        return redirect(url_for('main.index'))


@thread_blueprint.route("<string:category_slug>")
def category_threads(category_slug):
    category = Category.query.filter_by(slug=category_slug).first_or_404()

    page = request.args.get('page', 1, type=int)

    threads = Thread.query\
                    .filter_by(category_id=category.id)\
                    .order_by(Thread.created_at.desc())\
                    .options(joinedload(Thread.category))\
                    .options(joinedload(Thread.comments))\
                    .paginate(page=page, per_page=10, error_out=False)

    return render_template('main/index.html', threads=threads)



@thread_blueprint.route("<string:category_slug>/<string:thread_slug>", methods=["GET", "POST", "DELETE", "PUT"])
def show(category_slug, thread_slug):
    category = Category.query.filter_by(slug=category_slug).first_or_404()
    thread = Thread.query\
        .filter_by(category_id=category.id, slug=thread_slug)\
        .first_or_404()

    if request.method == "GET":
        thread.update({"views_count": thread.views_count + 1})

    # Support for method overriding via _method query arg or form field
    method = request.args.get('_method', request.method).upper()
    if method == "DELETE":
        if thread.is_owner(current_user):
            thread.delete()
            flash("Your question has been deleted successfully", "success")

            return redirect(url_for('main.index'))
        else:
            abort(403)
        
    if method == "PUT":
        if thread.is_owner(current_user):
            thread.update({
                "title": request.form['title'],
                "slug": slugify(request.form['title']),
                "category_id": request.form['category_id'],
                "content": request.form['content']
            })

            flash("Your question has been updated successfully", "success")

            return redirect(url_for('threads.show', category_slug=thread.category.slug, thread_slug=thread.slug))
        else:
            abort(403)

    return render_template("threads/show.html", thread=thread)


@thread_blueprint.route("<string:category_slug>/<string:thread_slug>/edit")
@login_required
def edit(category_slug, thread_slug):

    category = Category.query.filter_by(slug=category_slug).first_or_404()
    thread = Thread.query.filter_by(category_id=category.id, slug=thread_slug).first_or_404()

    if not thread.is_owner(current_user):
        abort(403)

    thread_form = ThreadCreationForm()

    thread_form.title.data = thread.title
    thread_form.category_id.data = thread.category_id
    thread_form.content.data = thread.content
    thread_form.submit.label.text = "Edit"

    return render_template("threads/edit.html", thread=thread, form=thread_form)
