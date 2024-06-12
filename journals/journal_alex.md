# Week 15 

### Evidence:
Mark all that applied this week
- [x] Attended class
- [ ] Responded to PRs/Issues
- [ ] Met with the team online. Forum ______
- [ ] Committed to group repo

### Notes:
Discussed the user stories
As a blind person, I would like;
- I want to know the progress of any loading.
- I often get weird special character read out when I watch coding video
  (that are not used in any programming languages). I want them filtered out.
- It is frustrating to use a complicated application. I want a simple application with minimal interactions.
- To be added...(refer to [persona.md](../design/persona.md))

Took time to read through the project. Our team discussed and came up with how we can contribute to the user interaction.  
We decided that we will pre-process the video rather than to capture the code everytime.  

Taehyun(Alex) -> Add auditory feedback for pre-processing progress.  
Kok Wei -> Work on the pre-processing and extracting codes from the video.  
Jayden -> Add regex function to filter out special characters that is not related to programming languages.  
Vinh -> Noticed that code uses os.path. Change it to Pathlib for cross-platform compatibility.  
Alicia -> Team leader, will manage tasks and review them.


# Week 16

### Evidence:
Mark all that applied this week
- [x] Attended class
- [ ] Responded to PRs/Issues
- [ ] Met with the team online. Forum ______
- [x] Committed to group repo

### Notes: 
Worked on a branch named 'feature/auditory-feedback'  
I created an 'auditory-feedback.html' file where the progress will be audibly displayed to enable the program to read out
the information.
Additionally, I added a function that triggers a sound during the pre-processing of the video.  
While waiting for the pre-processing to complete, I've temporarily inserted a placeholder duration of 15 seconds.
However, this will be substituted with the actual progress of the pre-processing.



# Week 17 

### Evidence:
Mark all that applied this week
- [x] Attended class
- [ ] Responded to PRs/Issues
- [ ] Met with the team online. Forum ______
- [x] Committed to group repo

### Notes:
Alicia, our team leader, brought to my attention a bug in the auditory feedback feature.  
It functions well when uploading saved videos, but it failed to activate when inserting Youtube links.  
After addressing the issue, I made sure that both uploading saved videos and using Youtube links will now activate
the auditory feedback feature as intended.


# Week 18

### Evidence:
Mark all that applied this week
- [x] Attended class
- [ ] Responded to PRs/Issues
- [ ] Met with the team online. Forum ______
- [ ] Committed to group repo

### Notes: 
As a team, we have updated the program to perform video processing and code extraction in the background
rather than through the auditory_feedback.html interface.  
Additionally, we collaborated to enhance the player.html interface by incorporating timestamps and displaying 
extracted code to appear on the right side of the screen.  
These timestamps are designed to facilitate navigation through the video content and corresponding code segments.  
We want to use tab and shift + tab to navigate through the timestamps which will read out, and when the user presses
enter, it will synchronise with the video and the extracted code.
