# BookmarksAPI
A bookmark manager API that allows for simple bookmark management. User creation and authentication with access tokens, adding bookmarks, updating, deleting, and viewing existing bookmarks are all features. It also offers bookmark link visit tracking and statistics.

Read the docs [here](https://develiebookmarks-api.herokuapp.com/docs)

# Installation

1. Navigate into your desired folder, then clone this repo as shown, remember the dot (.) so as to avoid duplicating this repo's name again.

`git clone https://github.com/Dev-Elie/BookmarksAPI.git .`

2. Change to that specific directory

`cd directory path`

3. Install the requirements from the requirements.txt file.

`pip install -r requirements.txt`

4. Create a `.env` file in the root of the directory then add the following contents, adding values for each depending on your configs.

```
DATABASE_HOSTNAME=
DATABASE_PORT=
DATABASE_PASSWORD=
DATABASE_NAME=
DATABASE_USERNAME=
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=
```
5. Run a database migration

` alembic upgrade head`

6. Start the server

`uvicorn app.main:app --reload`
