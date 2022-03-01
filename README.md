
Current WIP: https://pacific-river-36151.herokuapp.com/index

# How do I run this locally?

You can run this with a local MongoDB, but since we're still developing this and that can be a bit onerous:

1. First, ask Val for a MongoDB URI (it's under my MongoDB Atlas account.)
2. Create a .env file and save this as `MONGODB_URI` in it along with the PORT `8080`, e.g.:
```
touch survey/.env
echo "MONGODB_URI=<value you got>" > survey/.env
echo "PORT=8080" >> survey/.env
```
> **_NOTE:_**  If you accidentally commit this .env publicly you expose the database credentials. That's why we use a .gitignore. It might not matter here, but let Val know so she can rotate the keys. It happens to the best of us. :)
3. Download the subfolder's python (pip install -r survey/requirements.txt, maybe in a python virtual environment)
3. Run main.py (`python survey/main.py`)
4. Open up [0.0.0.0:8000](0.0.0.0:8080) your web browser

Import things that need to be added:
- [ ] Existing values as default in survey.html jinja template
- [ ] Existing data to a database
- [ ] More friendly UI (more views for errors, after submission, etc.)
- [ ] If this were going to be more production-ready: handling users, handling "final" user submission
- [ ] Deciding on iframe, a link on the page, or a fancy collapsing iframe
