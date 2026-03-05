from dotenv import load_dotenv
from interface import build_interface

load_dotenv() 

if __name__ == "__main__":
    demo = build_interface()
    demo.launch()