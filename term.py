import os
import p2
import subprocess as sub
output = os.popen("ls -t | head -n1 |awk '$0'").read()
import re
try:
	output = output.strip()
	print(output)
	s = ""
	if(re.findall(r"py$",output)):
		s = "python3 "+output
	elif(re.findall(r"java$",output)):
		s = "javac " + output
	elif(re.findall(r"cpp$",output)):
		s = "g++ " + output
	elif(re.findall(r"c$",output)):
		s = "gcc " + output
	print(s)
	if(s != ""):
		s+=" 2> a1.txt"
		k=os.system(s)
		with open ("a1.txt","r") as f:
			s1=f.read()
			m=re.findall(r'.*?[eE]rror:.*',s1)
			for i in m:
				res = p2.mainFunction(i)
except Exception as e:
	print (e)
	

