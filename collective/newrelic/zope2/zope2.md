Introduction
------------
To enable 'start up' instrumentation, we cannot rely on pure monkey patching.
Main reason is that this product cannot be loaded in such a way, that we can patch what we -need- to patch before it's happening.

For now, this is a manual patch. We need to patch the following file:

    Zope2/Startup/run.py

The function we will patch is the 'prepare' function of Zope2.Startup.ZopeStarter. But it's imported in the 'run' function.
Making it impossible for us to monkeypatch it any other way then this (to my knowledge).
This is still work in progress and under research. But for now, change the run function to look like this.
This loads the configuration and monkey patches zope2 at the right time.

    def run():
        """ Start a Zope instance """
        import Zope2.Startup
        from collective.newrelic import config # Addition
        import collective.newrelic.zope2  # Addition
        starter = Zope2.Startup.get_starter()
        opts = _setconfig()
        starter.setConfiguration(opts.configroot)
        try:
            starter.prepare() # Patched!
        except:
            starter.shutdown()
            raise
        starter.run()

Also importantly, we need to raise the startup timeout, else the webtransaction will not be started!
And you will not see any results.
For example:

    [instance0]                                                                    
    recipe = collective.recipe.zope2cluster 
    ...
    environment-vars =   
        ...
        NEW_RELIC_STARTUP_TIMEOUT 10 
        ...