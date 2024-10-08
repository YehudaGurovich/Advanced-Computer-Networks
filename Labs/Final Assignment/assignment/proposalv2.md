# CTF Challenge Proposal

**_Created by Yehuda Gurovich_**

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
- **Topic 3**: _Self-hosted websites and domains_
- **Topic 4**: _Google Cloud Platform_
- **Topic 5**: _Docker_ containers for hosting websites

---

## Stage 2: Finding the Secret Route

### Description & Purpose

This stage involves discovering a hidden route on the website and downloading an executable file essential for the next stage.

### Steps Taken

1. **Step 1**: Examine the "Our Services" section on the homepage. Noting that each line starts with a capital letter, combine these letters to form the word "CURL."
2. **Step 2**: Use the `curl` command on the website to reveal a hidden message. The message contains words with extra spacing. Combining these words reveals: "route is secret mission". This indicates the secret route: [ctf.yehudagurovich.com/secretmission](http://ctf.yehudagurovich.com/secretmission).
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
3. **Step 3**: Follow the UDP stream for the packets in Wireshark to extract the transmitted message.

### Result

Participants obtain an encrypted message from the network traffic.

### Relevant Course Material & Other Tools and Techniques Used

- **Topic 1**: Creating _executable_ files using _pyinstaller_ in python
- **Topic 2**: Using _Wireshark_ for network analysis
- **Topic 3**: Understanding the _UDP_ protocol and packet analysis
- **Topic 4**: Performing _MITM attacks_ to capture network traffic
- **Topic 5**: _Threading_ to handle client and server at the same time when packets get sent in the executable
- **Topic 6**: _Sockets_ for the client and server
- **Topic 7**: _Scapy_ to generate all the packets

---

## Stage 4: Decrypting the Message & Final Message

### Description & Purpose

In this final stage, participants must decrypt the message obtained from the previous stage and decode it to reveal the final message.

### Steps Taken

1. **Step 1**: Analyze the length, cipher type, key, and encoding of the captured message.
2. **Step 2**: Figure out what parts of the message are useful and need to be ordered, in our case we need the last 21 characters if it ends with ctfXX where XX are the numbers for the order of the packet
3. **Step 3**: Use Python to decrypt the message using the Columnar Transposition Cipher and Base64 decoding.
4. **Step 4**: Visit [ctf.yehudagurovich.com/finalmessage](http://ctf.yehudagurovich.com/finalmessage) to access the final message.

### Result

Participants successfully complete the CTF challenge by decrypting and decoding the final message and then visiting the designated website to view the result.

### Relevant Course Material & Other Tools and Techniques Used

- **Topic 1**: Understanding and applying _ciphers_
- **Topic 2**: Techniques for _encryption and decryption_
- **Topic 3**: _Python programming_ for cryptographic tasks
- **Topic 4**: _Regex_ for filtering data
