import requests
from datetime import datetime, timedelta

class WebSocketBSS:

    def __init__(self):
        self.isInit = False
        self.api_url = "http://localhost:10302/command"
        self.headers = {
            "Content-Type": "application/json"
        }

    def beamstopper(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"BeamStop.insert",
                "param":""
            }

        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"BeamStop.remove",
                "param":""
            }

        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()
    
    def collimator(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"Collimator.insert",
                "param":""
            }
        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"Collimator.remove",
                "param":""
            }
        
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def light(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"BackLight.on",
                "param":""
            }
        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"BackLight.off",
                "param":""
            }
        
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def intensityMonitor(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"IntensityMonitor.on",
                "param":""
            }

        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"IntensityMonitor.off",
                "param":""
            }

        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

if __name__ == "__main__":
    ws = WebSocketBSS()
    print(ws.beamstopper("on"))
    print(ws.collimator("on"))
    print(ws.intensityMonitor("on"))
    print(ws.light("on"))
    print("######################")
    print(ws.beamstopper("off"))
    print(ws.collimator("off"))
    print(ws.intensityMonitor("off"))