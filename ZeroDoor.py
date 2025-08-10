#!/usr/bin/env python3
import logging
from ZeroMain import ZeroMain
from ZeroGUI import ZeroGUI

def main():
    # Initialize main controller
    controller = ZeroMain()
    
    # Initialize GUI with controller
    gui = ZeroGUI(controller)
    
    # Start GUI
    gui.run()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("zeroweb.log"),
            logging.StreamHandler()
        ]
    )
    main()