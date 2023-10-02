# from pathlib import Path
# import sys
# project_home = Path('home','app')
# if project_home not in sys.path:
    # sys.path = [project_home] + sys.path


from app import app
application = app.server