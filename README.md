# BF1 Bot Mod (OpenBF1)
Unofficial addon for Battlefield 1 which allow players to play match with Bots  
**Status: WIP**  
_______________
This is a community project that aims to add offline bots to BF1. The initial idea behind this project was to reverse engineer BF1 using techniques such as disassembly to add the existing single-player functionality to BF1's multiplayer mode.

Since this project has deviated significantly from the original goal of "adding bot functionality to BF1," I think it's better to upgrade the project name from "BF1 Bot Mod" to "OpenBF1-BF1 Bot Mod" to clearly indicate that this project is a miniature reconstruction of BF1.
  
<img width="100%" alt="BF1 Bot Mod - Main Menu" src="https://github.com/user-attachments/assets/a8ff28db-45e7-42fc-98c8-98c3ad844291" />  
  
<img width="100%" alt="BF1 Bot Mod - Main Menu (Custom Battle)" src="https://github.com/user-attachments/assets/12c24fc8-3724-4325-9063-a2c7f141a380" />
  
![BF1 Bot Mod - Main Menu (Terrain Editor)](https://github.com/user-attachments/assets/320f93d3-c9fa-427b-a2de-e089f60b2877)

However, I underestimated the complexity of the Frostbite engine, a complexity that made it impossible for me to do this through the original reverse engineering.
  
Although both BF4 and BF1 use the Frostbite engine, BF4 uses the earlier Frostbite 3 engine, which already has a mature VU framework. This is why BF4 can directly develop bot mods. BF1's Frostbite 3 engine, on the other hand, has been completely rebuilt, and its underlying logic is more complex, making it very difficult to modify from the outside.

Simply put, BF4 was able to create bot mods because it stood on the shoulders of giants (the VU framework), while BF1 lacked such giants. This prevented BF1 from using reverse engineering techniques to do so (BF1 used the Frostbite engine, which underwent a very complex reconstruction).

Therefore, I decided to rewrite a miniature BF1 engine with the help of cutting-edge technologies such as OpenGL. This engine is only used to implement the traditional functions of BF1 (conquest site mode involving infantry, vehicles, and aircraft). 

Due to a lack of extensive BF1 map resources, I am unable to build complete maps (such as Verdun, the Bloodstained Banquet Hall, and other well-known maps) within this miniature version of BF1. I hope you understand.
