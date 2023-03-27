# Configuration file for jupyter-notebook.

# Supply overrides for the tornado.web.Application that the Jupyter notebook
# uses.  
# 
# Large files will be difficult for the browser to load, so we limit it to 10 MB.

c.NotebookApp.tornado_settings = {"websocket_max_message_size": 1024*1024*10}
