# Friends Forever

## Table of Contents

* [Summary](#summary)
* [Tech Stack](#tech-stack)
* [Features](#features)
* [Setup/Installation](#setup)
* [About the Developer](#developer)

## <a name="summary"></a>Summary
**Friends Forever** is a social media web app geared towards retirees. It allows retirees to locate other users in their areas, or other cities to connect with and build social network. A TicketMaster API has also been implemented to allow users to search events by state and its major cities.

See the <a href="#">Demo Reel.</a>

## <a name="tech-stack"></a>Tech Stack
__Front End:__ HTML5, Jinja2, CSS, JavaScript, AJAX, jQuery, Bootstrap<br/>

__Back End:__ Python, Flask, PostgreSQL, SQLAlchemy <br/>

## <a name="features"></a>Features

Register account.

![Register GIF](/static/images/register.gif)

Create and Log in to an account.

![Login GIF](/static/images/login.gif)

Users can comments and replies to comments.

![Comments and Posts GIF](/static/images/comments_replies.gif)

Users can search for other users and certain posts.

![Custom Stitch GIF](/static/images/search.gif)

Search events by querying the Ticketmaster API.

![Search Events GIF](/static/images/search_events.gif)

Delete users and/or posts as Admin.

![Admin GIF](/static/images/admin.gif)

Log out from Friends Forever. 

![Logout GIF](/static/images/logout.gif)

## <a name="setup"></a>Setup/Installation

#### Requirements:

- Python 3.10.0
- PostgreSQL

To run this app on your local computer, follow these steps:

Clone repository:
```
$ git clone https://github.com/skaur1027/friends_forever
```

Create a virtual environment:
```
$ virtualenv env
```

Activate the virtual environment:
```
$ source env/bin/activate
```

Install dependencies:
```
$ pip3 install -r requirements.txt
```

To run Flask you need to set a secret key. Create a 'secrets.sh' file in the project directory and add a key.

Add the key to your environmental variables (do this each time you restart your virtual environment):
```
$ source secrets.sh
```

Create database 'social_app':
```
$ createdb social_app
```

Create your database tables:
```
$ python3 models.py
```

Run app from the command line:
```
$ python3 server.py
```

Visit localhost:5000 on your browser.

## <a name="developer"></a>About the Developer

Sandeep Singh (she/her) has a background in Business Administration, with a degree in Human Resources. She loves to learn new skills, learn about new topics, and loves to spend time with family. She always tries to help her family out as much as she can. The inspiration behind this web app is her father, a current retiree.
You can learn more about her on her <a href="https://www.linkedin.com/in/sandeep-kaur-singh/">LinkedIn.</a>