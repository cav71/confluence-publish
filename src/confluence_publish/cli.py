import argparse
import logging


class Argument:
    def __init__(self, remove=None):
        self._remove = remove

    def add_arguments(self, **kwargs):
        pass

    def process(self, options):
        return

    def remove(self, options):
        if not self._remove:
            return
        for k in self._remove:
            delattr(options, k)


class ArgumentParser(argparse.ArgumentParser):
    class NotAssigned:
        def __init__(self, value):
            self.value = value
            self.asiterable = None
        def __str__(self):
            return str(self.value)

        def __copy__(self):
            from copy import copy
            if self.asiterable and self.value is None:
                return []
            return copy(self.value)

    def __init__(self, *args, **kwargs):
        class MyFormatter(
            argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
        ):
            pass
        kwargs["formatter_class"] = kwargs.get("formatter_class", MyFormatter)
        super(ArgumentParser, self).__init__(*args, **kwargs)

        self._xarguments = []
        self.argument_default = self.NotAssigned(None)

    def add_argument(self, *args, **kwargs):
        if "default" in kwargs and kwargs.get("default") != argparse.SUPPRESS:
            kwargs["default"] = self.NotAssigned(kwargs.get("default"))
        if len(args) and (type(args[0]) is type) and issubclass(args[0], Argument):
            self._xarguments.append(args[0]())
            self._xarguments[-1].add_arguments(self, **kwargs)
            return
        argument = super(ArgumentParser, self).add_argument(*args, **kwargs)
        if kwargs.get("action") in { "append_const"}:
            argument.default.asiterable = True
        return argument

    def parse_known_args(self, args, namespace):
        args, argv = super(ArgumentParser, self).parse_known_args(args, namespace)

        if self._xarguments and isinstance(self._xarguments[0], ConfigArgument):
            args = self._xarguments[0].process(args) or args
            self._xarguments[0].remove(args)
            del self._xarguments[0]

        for k in dir(args):
            if k.startswith("_"):
                continue
            if isinstance(getattr(args, k), self.NotAssigned):
                setattr(args, k, getattr(args, k).value)

        for a in self._xarguments:
            try:
                args = a.process(args) or args
            except (TypeError, ValueError, argparse.ArgumentTypeError) as e:
                self.error(e)
            a.remove(args)
        return args, argv


class ConfigArgument(Argument):
    def __init__(self):
        super(ConfigArgument, self).__init__(remove={"config", "config_key"})

    def add_arguments(self, parser, **kwargs):
        parser.add_argument("-c", "--config")
        parser.add_argument("-k", "--config-key")

    def process(self, options):
        conffile = options.config
        if isinstance(options.config, ArgumentParser.NotAssigned):
            conffile = options.config.value
        confkey = options.config_key
        if isinstance(options.config_key, ArgumentParser.NotAssigned):
            confkey = options.config_key.value

        if conffile:
            with open(conffile) as fp:
                config = json.load(fp)
            if confkey:
                config = config[confkey]
            for key, value in config.items():
                if isinstance(options.__dict__.get(key), ArgumentParser.NotAssigned):
                    options.__dict__[key] = value


class LoggingArguments(Argument):
    def __init__(self):
        super(LoggingArguments, self).__init__({"loglevel"})
        self.quiet = True

    def add_arguments(self, parser, **kwargs):
        parser.add_argument("-v", "--verbose", dest="loglevel", action="append_const", const=1)
        parser.add_argument("-q", "--quiet", dest="loglevel", action="append_const", const=-1)
        self.quiet = kwargs.pop("quiet") if "quiet" in kwargs else self.quiet

    def process(self, options):
        loglevel = sum(options.loglevel or []) - int(self.quiet)
        print(options, loglevel)
        if loglevel < 0:
            level = logging.WARNING
        elif loglevel == 0:
            level = logging.INFO
        else:
            level = logging.DEBUG
        logging.basicConfig(level=level)


