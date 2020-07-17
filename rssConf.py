import sys
import configparser



class Conf:

    def __init__(self, fileName):
        self.configFN = fileName
        self.config = configparser.ConfigParser()
        self.config.read(self.configFN)

    def getSections(self):
        self.sections = self.config.sections()
        return(self.sections)

    def getItemsInSection(self, section):
        self.items = self.config.items(section)
        return(self.items)

    def getItem(self, section, entry):
        self.entry = self.config[section][entry]
        return(self.entry)



def main(argv):

    print('started')

    configFN = 'rss.conf'
    conf = Conf(configFN)

    sections = conf.getSections()
    print('sections: ', sections)

    items = conf.getItemsInSection('PROD')
    print('all items in prod: ', items)

    item = conf.getItem('PROD', 'DEFAULT_FEED')
    print('feed: ', item)

    print('stopped')



if __name__ == '__main__':
    main(sys.argv)
