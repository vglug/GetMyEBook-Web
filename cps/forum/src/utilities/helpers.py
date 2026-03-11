from datetime import datetime
from cps.forum.database.models.category import Category
from cps.forum.src.cache import Cache

def now():
    return datetime.now()


def cached_categories():
    cache = Cache()
    categories = cache.get("categories")

    if categories is None:
        # Load all categories from DB
        db_categories = Category.query.all()
        
        # If DB is empty, run seeder to load 4 default categories
        if not db_categories:
            try:
                from cps.forum.database.seeds.category_seeder import categories_run
                categories_run()
                db_categories = Category.query.all()
            except ImportError:
                # Fallback if seeder cannot be imported
                pass

        categories = list(
            map(lambda category: category.to_json(), db_categories)
        )

        cache.set("categories", categories, timeout=5*60)

    return categories



