# CTF Challenge Proposal

#### Yehuda Gurovich - ```44184491```

## Stage 1: Setup & Start

### Description & Purpose

In this initial stage, participants are introduced to the challenge by visiting the provided website to gather background information.

### Steps Taken

1. **Step 1**: Navigate to [ctf.yehudagurovich.com](http://ctf.yehudagurovich.com) to access the starting page of the CTF.

### Result

Participants can view the homepage of the website and begin their exploration.

### Relevant Course Material & Other Tools and Techniques Used

- **Topic 1**: Basics of a _Python HTTP server_
- **Topic 2**: Understanding _sockets_ used in HTTP servers
- **Topic 3**: _Self-hosted websites and domains_, specifically on Google Cloud Platform

---

## Stage 2: Finding the Secret Route

### Description & Purpose

This stage involves discovering a hidden route on the website and downloading an executable file essential for the next stage.

### Steps Taken

1. **Step 1**: Examine the "Our Services" section on the homepage. Noting that each line starts with a capital letter, combine these letters to form the word "CURL."
2. **Step 2**: Use the `curl` command on the website to reveal a hidden message. The message contains words with extra spacing. Combining these words reveals: "route is secret message". This indicates the secret route: [ctf.yehudagurovich.com/secretmessage](http://ctf.yehudagurovich.com/secretmessage).
3. **Step 3**: Access the hidden route to download the necessary executable file.

### Result

Participants obtain the executable file required for the subsequent stage.

### Relevant Course Material & Other Tools and Techniques Used

- **Topic 1**: Basics of a _Python HTTP server_
- **Topic 2**: Understanding _sockets_ used in HTTP servers
- **Topic 3**: Techniques for _self-hosting websites and domains_, using Google Cloud Platform
- **Topic 4**: Utilizing _curl_ to interact with web servers
- **Topic 5**: Analyzing _HTTP user agents_ and headers

---

## Stage 3: Executing the File & MITM Attack

### Description & Purpose

This stage involves running the executable file, observing network traffic, and performing a Man-in-the-Middle (MITM) attack to capture a transmitted message.

### Steps Taken

1. **Step 1**: Execute the downloaded file and monitor network traffic to observe packet transmissions.
2. **Step 2**: Use Wireshark to capture and analyze the network packets.
3. **Step 3**: Trace the UDP packets in Wireshark to extract the transmitted message.

### Result

Participants obtain an encrypted message from the network traffic.

### Relevant Course Material & Other Tools and Techniques Used

- **Topic 1**: Working with _executable_ files
- **Topic 2**: Using _Wireshark_ for network analysis
- **Topic 3**: Understanding the _UDP_ protocol and packet analysis
- **Topic 4**: Performing _MITM attacks_ to capture network traffic

---

## Stage 4: Decrypting the Message & Final Message

### Description & Purpose

In this final stage, participants must decrypt the message obtained from the previous stage and decode it to reveal the final message.

### Steps Taken

1. **Step 1**: Analyze the length, cipher type, key, and encoding of the captured message.
2. **Step 2**: Use Python to decrypt the message using the Columnar Transposition Cipher and Base64 decoding.
3. **Step 3**: Visit [ctf.yehudagurovich.com/finalmessage](http://ctf.yehudagurovich.com/finalmessage) to access the final message.

### Result

Participants successfully complete the CTF challenge by decrypting and decoding the final message and then visiting the designated website to view the result.

### Relevant Course Material & Other Tools and Techniques Used

- **Topic 1**: Understanding and applying _ciphers_
- **Topic 2**: Techniques for _encryption and decryption_
- **Topic 3**: _Python programming_ for cryptographic tasks
