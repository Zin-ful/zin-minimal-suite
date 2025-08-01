DUE TO RECENT YOUTUBE CENSORSHIP I WILL BE FOCUSING ON CREATING A SELF-HOSTED ALTERNATIVE

The C webserver (minimal, made to run on very low end devices to act as an online streaming service)
will be remade either in C still, or python. It will be remade to include heavier and more convient features
like thumbnails, fast forward (by speed), and a few other things. For info on how to make both services work,
check their github


This software is to make low-end linux devices easy and effective to use
the main issue is that the software is designed to work with itself, not to intergrate with existing software
Along with this, these programs will have varients that suite off-grid needs (communicating over LoRa)
this repo will be updated around every few weeks or so when ive made enough progress to worry about losing it

most if not all code is written in python for its memory management and networking
if your looking for even lighter C projects check out the C webserver, made for video streaming.

For use on CLI systems, early in dev so dont expect a ton for a bit

All CLI programs will be converted to curses and updated with new features
the CLI versions are just a base for the curses to build on and are usually abandoned.
However, after a program is fully completed i will end up remaking the CLI versions to match
along with this will be versions for LoRa (packet size limitations)