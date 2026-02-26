# Traffic Light Raspberry Pi Code
# Copyright(c) 2026 Luna Moonlit Noir | The Unlicense

# This code is for a school project.
# The reason this is unlicense is because of how unimportant and unuseful this is.
# If you want, do whatever with this. I don't really care.
# I will not be held liable for this.

# "type: ignore" is to tell python's strict type annotation to ignore that line

from gpiozero import LED, Button # type: ignore # Standard GPIO input and output
import asyncio as asy # For asynchronous functions

class TrafficLight: # Main Traffic Light code
    def __init__(self) -> None: # Inital code once function is called in TrafficLight
        self.red: LED = LED(17) # Stop
        self.amber: LED = LED(27) # Prepare to Stop
        self.green: LED = LED(22) # Proceed when safe
        self.ped_light: LED = LED(24) # Allow pedestrians to cross
        self.button: Button = Button(23) # Pedestrian crossing request

        self.state: str = "RED" # Start as RED (Stop)

        self.queued: bool = False # Start unqueued for peds

    async def ped(self) -> None: # Pedestrial Request
        while True:
            if self.button.is_pressed: # type: ignore # When pedestrian requests crossing
                self.queued = True # Queue pedestrial
            await asy.sleep(0.1) # Wait 0.1 seconds (100 milliseconds) to avoid lag
            
    async def ped_update(self) -> None: # Update pedestrian light when light is RED
        if self.queued:
            self.ped_light.on() # Solid on, 30 seconds on start
            await asy.sleep(10) # Wait 10 seconds, 20 seconds after await
            for _ in range(1, 30): # Ever 0.5 seconds toggle on off, leave 5 seconds off before light is GREEN
                self.ped_light.off()
                await asy.sleep(0.5)
                self.ped_light.on()
                await asy.sleep(0.5)

    def check_state(self) -> None: # Check Traffic Light state
        match self.state:
            case "RED": # Stop
                if self.queued: # Allow crossing if queued
                    _ = self.ped_update()
                self.red.on()
                self.amber.off()
                self.green.off()
            case "AMBER": # Prepare to stop
                self.red.off()
                self.amber.on()
                self.green.off()
            case "GREEN": # Proceed when safe
                self.red.off()
                self.amber.off()
                self.green.on()
            case _: # Unused
                pass

    async def cycle(self) -> None: # Traffic Light cycle
        while True:
            self.check_state() # Check state after changes
            
            match self.state:
                case "RED": # If RED, wait 30 seconds, change to GREEN
                    await asy.sleep(30)
                    self.state = "GREEN"
                case "AMBER": # If AMBER, wait 5 seconds, change to RED
                    await asy.sleep(5)
                    self.state = "RED"
                case "GREEN":
                    await asy.sleep(25) # If GREEN, wait 5 seconds, change to AMBER
                    self.state = "AMBER"
                case _: # Unused
                    pass
                
    async def main(self) -> None: # Main class entry
        await asy.gather(self.cycle(), self.ped(), self.ped_update()) # Initialize async functions.
                
if __name__ == "__main__": # Main code entry
    tl = TrafficLight() # Instance TrafficLight
    try:
        asy.run(tl.main()) # Start TrafficLight
    except KeyboardInterrupt:
        exit(0) # If recieve KeyboardInterrupt (CTRL+C) from testing, exit normally.
    except Exception as e:
        exit(1) # If for some reason TrafficLight.main() does not start, exit with an error code. It should never reach this point.