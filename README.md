# [Link to the newer demo video](https://www.reddit.com/r/developersIndia/comments/1n6w0ao/for_a_hackathon_made_a_c_debugger_frontend_in_an/)

## How to run this project

Please download GDB beforehand. Methods may vary, so I'm not including that.

Clone this repo, then run this command (make sure that you have Python installed):

`$ pip install -r requirements.txt`

[If you face any problems while installing packages using Python, search with the name of your OS/Distro and the error. For example, in Ubuntu-based distros, using pipx instead of pip is sufficient for our use case.]

Then, while you're on the base directory, run:

`$ flask run`

Go to the link it redirects towards.

That's it :)

## Inspiration

We wanted to help newcomers to C understand how pointers work, since it’s a concept that many people find confusing.

## What it does

Most of the website contains standard educational material. The unique feature is a debugger that allows you to run a program and see what happens step by step.

## How we built it

I used pygdbmi (a Python package for GDB’s Machine Interface) to build the core of the debugger. From there, I wrote helper functions, which were then called through a Flask app whenever an API request was made. The API was triggered by JavaScript, which also updated the HTML with the debugger’s output.

## Challenges we ran into

I/O buffering caused issues with printing output. GDB’s Machine Interface required pseudo-terminals to display output, but I didn’t want to create a new TTY because multithreading would make things complicated. At the same time, I didn’t want to print everything in the same terminal because that would quickly become cluttered.

We also had to handle race conditions, which we solved using a delay loop in _treat_response inside helper.py. Another challenge was debugging the “Run to End” button from the frontend perspective, which proved tricky.

## Accomplishments that we're proud of

We successfully implemented a debugger from scratch, relying almost entirely on documentation. (Seriously, if you search for “pygdbmi” and check the Videos section, you’ll find only two videos about it.)

## What we learned

We gained a deeper understanding of how the GDB debugger works, especially the GDB Machine Interface.

## What's next for C Memory and Visualization

I plan to continue developing the project and will keep the current version in a separate branch.


