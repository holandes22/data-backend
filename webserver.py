import cherrypy
from data_api.wsgi import application


if __name__ == '__main__':
    cherrypy.tree.graft(application, '/')
    # Unsuscribe the default server
    cherrypy.server.unsubscribe()
    server = cherrypy._cpserver.Server()
    server.socket_host = '0.0.0.0'
    server.socket_port = 80
    server.thread_pool = 30
    server.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()

