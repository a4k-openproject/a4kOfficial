import time

from providerModules.a4kOfficial import common


class Core:
    def __init__(self):
        self.start_time = time.time()
        self.sources = []
        self._scraper = self.__module__.split('.')[-1]

    def _return_results(self, source_type, sources, preemptive=False):
        if preemptive:
            common.log(
                "a4kOfficial.{}.{}: cancellation requested".format(
                    source_type, self._scraper
                ),
                "info",
            )
        common.log(
            "a4kOfficial.{}.{}: {}".format(source_type, self._scraper, len(sources)),
            "info",
        )
        common.log(
            "a4kOfficial.{}.{}: took {} ms".format(
                source_type, self._scraper, int((time.time() - self.start_time) * 1000)
            ),
            "info",
        )

        return sources

    def episode(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []

        return self._return_results("episode", sources)

    def movie(self, simple_info, all_info):
        self.start_time = time.time()
        sources = []

        return self._return_results("movie", sources)

    @staticmethod
    def get_listitem(return_data):
        list_item = xbmcgui.ListItem(path=return_data["url"], offscreen=True)
        list_item.setContentLookup(False)
        list_item.setProperty('isFolder', 'false')
        list_item.setProperty('isPlayable', 'true')

        return list_item
