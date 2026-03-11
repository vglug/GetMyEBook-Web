import smtplib

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("vasanth2005kk@gmail.com", "ziebqqoqushovgom")
print("Login successful")