# Traffic Light Raspberry Pi Code
# Copyright(c) 2026 Luna Moonlit Noir | The Unlicense

# This code is for a school project.
# The reason this is unlicense is because of how unimportant and unuseful this is.
# If you want, do whatever with this. I don't really care.
# I will not be held liable for this.

# "type: ignore" is to tell python's strict type annotation to ignore that line

from gpiozero import LED, Button # type: ignore # Standard GPIO input and output
import asyncio as asy # For asynchronous functions
import time

class TrafficLight: # Main Traffic Light code
    def __init__(self) -> None: # Inital code once function is called in TrafficLight
        self.red: LED = LED(17) # Stop
        self.amber: LED = LED(27) # Prepare to Stop
        self.green: LED = LED(22) # Proceed when safe
        self.ped_light: LED = LED(24) # Allow pedestrians to cross
        self.button: Button = Button(23) # Pedestrian crossing request

        self.state: str = "RED" # Start as RED (Stop)

        self.queued: bool = False # Start unqueued for peds
        
    def panic(self): # If error (excpetion) recieved
        self.amber.off() # Disable all lights except RED
        self.green.off()
        self.ped_light.off()
        
        try:
            while True: # Blinking Red Loop: Singal to treat as all-way stop sign.
                self.red.toggle()
                time.sleep(0.5)
        except KeyboardInterrupt: # Interrupt to exit.
            self.red.off()
            print("\nExiting...")
            return # Return without statement to return None (null)

    async def ped(self) -> None: # Pedestrial Request
        while True:
            if self.button.is_pressed and not self.queued: # type: ignore # When pedestrian requests crossing and not already queued
                self.queued = True # Queue pedestrial
                print("PED: Queued.")
            await asy.sleep(0.1) # Wait 0.1 seconds (100 milliseconds) to avoid lag
            
    async def ped_update(self) -> None: # Update pedestrian light when light is RED
        if self.queued:
            print("PED: Allowing cross...")
            self.ped_light.on() # Solid on, 30 seconds on start
            await asy.sleep(10) # Wait 10 seconds, 20 seconds after await
            for _ in range(1, 30): # Ever 0.5 seconds toggle on off, leave 5 seconds off before light is GREEN
                self.ped_light.off()
                await asy.sleep(0.5)
                self.ped_light.on()
                await asy.sleep(0.5)
            self.ped_light.off()

    async def check_state(self) -> None: # Check Traffic Light state
        match self.state:
            case "RED": # Stop
                print("TRAFFIC: RED light.")
                self.red.on()
                self.amber.off()
                self.green.off()
                if self.queued: # Allow crossing if queued
                    await self.ped_update()
            case "AMBER": # Prepare to stop
                print("TRAFFIC: AMBER light.")
                self.red.off()
                self.amber.on()
                self.green.off()
            case "GREEN": # Proceed when safe
                print("TRAFFIC: GREEN light.")
                self.red.off()
                self.amber.off()
                self.green.on()
            case _: # Unused
                pass

    async def cycle(self) -> None: # Traffic Light cycle
        while True:
            await self.check_state() # Check state after changes
            
            match self.state:
                case "RED": # If RED, wait 30 seconds, change to GREEN
                    await asy.sleep(5)
                    self.state = "GREEN"
                case "AMBER": # If AMBER, wait 5 seconds, change to RED
                    await asy.sleep(3)
                    self.state = "RED"
                case "GREEN":
                    await asy.sleep(5) # If GREEN, wait 5 seconds, change to AMBER
                    self.state = "AMBER"
                case _: # Unused
                    pass
                
    async def main(self) -> None: # Main class entry
        print("Starting...")
        await asy.gather(self.cycle(), self.ped()) # Initialize async functions.
                
if __name__ == "__main__": # Main code entry
    tl = TrafficLight() # Instance TrafficLight
    try:
        asy.run(tl.main()) # Start TrafficLight
    except KeyboardInterrupt:
        print("Stopping...")
        tl.panic()
        exit(1) # If recieve KeyboardInterrupt (CTRL+C) from testing, exit normally.
    except Exception as e:
        print("Panic: ", e)
        tl.panic()
        exit(1) # If for some reason TrafficLight.main() does not start, exit with an error code. It should never reach this point.