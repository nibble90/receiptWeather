from escpos import printer
from os import getenv
from dotenv import load_dotenv
from pyowm import OWM
from sys import exit
from newsapi import NewsApiClient

class ReceiptWeather:
    def __init__(self, dummy=False):
        try:
            load_dotenv(dotenv_path=".env")
            self.owm = OWM(getenv('OPENWEATHERAPIKEY'))
            self.city_id = int(getenv('WEATHERID'))
            self.newsAPI = NewsApiClient(api_key=getenv('NEWSAPIKEY'))
            self.print_array = []

            self.mgr = self.owm.weather_manager()
              
            self.p = printer.Usb(0x076c, 0x0303, 0, 0, 0x02) if not dummy else printer.Dummy()
            self.observation = self.mgr.weather_at_id(self.city_id)
            # Bus 002 Device 001: ID 04b8:0202 Epson ...
            # lsusb -vvv -d xxxx:xxxx | grep iInterface
            #       iInterface              0
            # lsusb -vvv -d xxxx:xxxx | grep bEndpointAddress | grep OUT
            #       bEndpointAddress     0x01  EP 1 OUT
            # = Usb.(0x04b8, 0x0202, 0, 0, 0x01)
            # OR = Usb.(0x04b8, 0x0202)
        except Exception as e:
            print(e)
            exit(1)

    def get_weather(self):
        message = "{}".format(self.observation.weather.detailed_status)
        return message

    def get_temperature(self):
        # {'temp', 'temp_max', 'temp_min', 'feels_like', 'temp_kf'}
        info = self.observation.weather.temperature('celsius')
        messages = [
        "Current Temperature : {}".format(info['temp']),
        "Feels Like          : {}".format(info['feels_like']),
        "Maximum Temperature : {}".format(info['temp_max']),
        "Lowest Temperature  : {}".format(info['temp_min'])]
        for message in messages: self.print_array.append(message)

    def get_header(self):
        messages = [
            "Weather at: {}".format(self.observation.reception_time('date').time()),
            "--------------------",
            "Condition: {}".format(self.get_weather())]
        for message in messages: self.print_array.append(message)

    def get_top_5_news(self):
        messages = self.newsAPI.get_top_headlines(sources='bbc-news')['articles']
        self.print_array.append("--------------------")
        for message in messages: messages = self.print_array.append(message['title'])

    def assemble_print(self):
        try:
            self.get_header()
            self.get_temperature()
            self.get_top_5_news()
            for message in self.print_array:
                self.p.text("{}\n".format(message))
            self.p.cut(mode='PART')
        except Exception as e:
            print(e)
            exit(1)

if __name__ == "__main__":
    dummy = True
    obj = ReceiptWeather(dummy=dummy)
    obj.assemble_print()
    if(dummy):
        print(obj.p.output.decode("utf-8"))
    print("done")
