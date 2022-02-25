from escpos import printer
from os import getenv
from dotenv import load_dotenv
from pyowm import OWM

class ReceiptWeather:
    def __init__(self):
        try:
            load_dotenv(dotenv_path=".env")
            self.owm = OWM(getenv('OPENWEATHERAPIKEY'))
            self.city_id = int(getenv('WEATHERID'))

            self.mgr = self.owm.weather_manager()
                        
            # self.p = printer.Usb(0x2730, 0x0fff, 0, 0x81, 0x02)
            self.p = printer.Dummy()
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

    def get_weather(self):
        message = "{}".format(self.observation.weather.detailed_status)
        return message

    def get_temperature(self):
        # {'temp', 'temp_max', 'temp_min', 'feels_like', 'temp_kf'}
        info = self.observation.weather.temperature('celsius')
        message = [
        "Current Temperature : {}".format(info['temp']),
        "Feels Like          : {}".format(info['feels_like']),
        "Maximum Temperature : {}".format(info['temp_max']),
        "Lowest Temperature  : {}".format(info['temp_min'])]
        return message

    def get_header(self):
        message = "Weather at: {}".format(self.observation.reception_time('date').time())
        return message

    def assemble_print(self):
        self.p.text("{}\n".format(self.get_header()))
        self.p.text("--------------------\n")
        self.p.text("Condition: {}\n".format(self.get_weather()))
        for message in self.get_temperature():
            self.p.text("{}\n".format(message))
        self.p.cut()

if __name__ == "__main__":
    obj = ReceiptWeather()
    obj.assemble_print()
    dummyoutput = obj.p.output
    print(dummyoutput.decode("utf-8"))