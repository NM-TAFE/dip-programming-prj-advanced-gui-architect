# Week 15 
### Mark all that applied this week
- [x] Attended class
- [ ] Responded to PRs/Issues
- [x] Met with the team online. Discord
- [x] Committed to group repo

### Other
I was assigned the task of changing how the keybindings work so that they wouldn't activate whilst typing in an input box

# Week 16
### Mark all that applied this week
- [ ] Attended class
- [ ] Responded to PRs/Issues
- [x] Met with the team online. Discord
- [ ] Committed to group repo

### Other
This week I went over the code to get a more in-depth understanding of it and I also looked into the preprocessing concept branch.

# Week 17
### Mark all that applied this week
- [ ] Attended class
- [ ] Responded to PRs/Issues
- [x] Met with the team online. Discord
- [ ] Committed to group repo

### Other
This week I experimented with different AI models to use (llama3, codellama and llava) to extract and format code from the video.
I created a test script to extract formatted code, an explanation of the formatted code and the timestamp of the code.

# Week 18
### Mark all that applied this week
- [x] Attended class
- [x] Responded to PRs/Issues
- [x] Met with the team online. Discord
- [x] Committed to group repo

### Other
This week I implemented my experimental preprocess script (credits to Low Kok Wei) into the OcrRoo program under the features/preprocessing-and-timestamps branch, as well as added multiple settings that change the behaviour of the preprocessing.
Some of the features this introduced are the following:
1. Preprocessing Videos
2. Enable / Disable Preprocessing
3. Toggle on/off formatted code and code explanations
4. Setting to change the preprocessing interval
5. Setting to change the llama endpoint (incase the user isn't locally hosting it, or is using a different port)
6. Timestamps detected to contain working code that appear below the media player whilst the video is processing. Once clicked, the video will go to that timestamp (planning to make this a lot nicer, didn't get to do that just yet though)

# Week 19
### Mark all that applied this week
- [x] Attended class
- [x] Responded to PRs/Issues
- [x] Met with the team online. Discord
- [x] Committed to group repo

### Other
This week I merged my experimental preprocessing branch and added a setting for the user to be able to alternate between llama and openai depending on which one they would like to use. Some other notable changes are:
1. If the user has preprocessing and formatted code enabled, the "Code Captures" section will turn into "Code Timestamps" and provide timestamps where code was detected, and the code detected at that timestamp.
2. Added a next timestamp and previous timestamp button, which will skip you to the next or previous timestamp relative to your current position in the video. We would've liked to modify the code timestamps sections to only display the relevant code, however I didn't get to implementing that just yet :(
