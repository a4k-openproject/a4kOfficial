from providerModules.a4kOfficial import common


class AddonNotInstalledError(Exception):
    def __init__(self, scraper, plugin):
        common.log(
            'a4kOfficial.{}: {} not installed.'.format(self._scraper, self._plugin),
            'error',
        )
