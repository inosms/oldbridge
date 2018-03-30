# based on
# https://stackoverflow.com/questions/27863832/calling-python-2-script-from-python-3
# https://github.com/pytest-dev/execnet/issues/26
#
# This is used to call python functions with another python version
#
# Use in the following way for example
#   bridge = Bridge(version="2.7", module="my_module", path="../path/to/source")
#   my_function = bridge.connect("my_function")
#   result = my_function(call,with,parameters,as,usual)
#
# Construction a bridge at first and then calling the .connect(str) function is done this
# way to be able to connect more then one function from a given module easily.
# keyworded argumetnts are not supported yet

import execnet
import sys
import os


class BridgeConnection:
    def __init__(self, version, module, function_name, path=None):
        self.version = version
        self.module = module
        self.function_name = function_name
        self.path = path

    def __call__(self, *args):
        gw = execnet.makegateway("popen//python=python%s" % self.version)

        script = """
                        import sys

                        outchan = channel.gateway.newchannel()
                        sys.stdout = outchan.makefile("w")
                        channel.send(outchan)
                        errchan = channel.gateway.newchannel()
                        sys.stderr = errchan.makefile("w")
                        channel.send(errchan)
                        """
        if self.path is not None:
            script += """
                        sys.path.append('%s')
                        """ % (os.path.abspath(self.path))
        script += """
                        from %s import %s as the_function

                        result = the_function(*channel.receive())

                        channel.send(result)

                        sys.stdout = sys.__stdout__
                        sys.stderr = sys.__stderr__
                        try:
                            sys.stdout.flush()
                            sys.stdout.close()
                        except:
                            pass
                        try:
                            sys.stderr.flush()
                            sys.stderr.close()
                        except:
                            pass

                        outchan.close()
                        errchan.close()
                        """ % (self.module, self.function_name)

        channel = gw.remote_exec(script)
        outchan = channel.receive()
        errchan = channel.receive()
        outchan.setcallback(lambda data: sys.stdout.write(str(data)))
        errchan.setcallback(lambda data: sys.stderr.write(str(data)))
        channel.send(args)
        result = channel.receive()
        # wait for proper shutdown
        # https://bitbucket.org/hpk42/execnet/issues/26/redirecting-stdout-stderr-in-the-remote
        outchan.waitclose()
        errchan.waitclose()
        return result


class Bridge:
    def __init__(self, version, module, path=None):
        self.version = version
        self.module = module
        self.path = path

    def __getattr__(self, item):
        return BridgeConnection(self.version, self.module, item, self.path)