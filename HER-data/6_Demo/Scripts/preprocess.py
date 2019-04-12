# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

""" USERS WILL NEED TO DEFINE WHAT TYPES OF ANNOTATIONS THEY WANT TO PRESERVE IF THERE IS PRE EXISTING ANNOTATION """

import sys
import fileinput
import string
import time

file = sys.argv[1]
extension = file.split('.')[-1]
file = open(file, encoding="utf-8", errors="backslashreplace")
file = file.read().splitlines()

####################### PREPROCESSING THE XML FILE #######################
if extension == 'xml':

	""" THE USER SHOULD DEFINE WHAT ANNOTATIONS THEY WANT TO PRESERVE HERE """
	labelMapping = {}
	# for x in 'place','oronym','building','geographical':
	# 	segStart = '<name type="'+x+'">'
	# 	labelMapping[segStart] = '$'
	segEnd = '</name>'
	bodyStart = '<p>'
	bodyStop = '</p>'
	###########################################################################


	body = False
	lookingForClosure = None

	### MAKE THE START AND STOPS OF BODY TEXT MORE RECOGNIZABLE VIA WORD SPLITTING
	for line in file:
		for x in labelMapping:
			line = line.replace(labelMapping[x],'')
		line = line.replace(bodyStart,' '+bodyStart+' ').replace(bodyStop,' '+bodyStop+' ').replace(segEnd,' '+segEnd+' ')
		segStarts = {}
		for segStart in labelMapping:
			line = line.replace(segStart,' '+labelMapping[segStart]+' ')
			segStarts[labelMapping[segStart]] = True
		words = []

		### GO THROUGH EACH WORD AND DETERMINE IF IT IS IN BODY OR NOT
		for word in line.split():
			if body:
				if word == bodyStop:
					body = False
				else:
					# PRESERVE ANNOTATIONS WITH A SINGLE CHARACTER MARKER, SPACE SEPARATED, BEFORE AND AFTER THE NAMED ENTITY
					if word in segStarts:
						lookingForClosure = word
						words.append(word)
					elif word == segEnd:
						if lookingForClosure != None:
							words.append(lookingForClosure)
							lookingForClosure = None
					else:
						words.append(word)

			elif word == bodyStart:
				body = True

		# FINALLY WE PROCESS REMAINING TEXT BY CHARACTER REMOVING META DATA WE DON'T NEED
		text = True
		if len(words) > 0:
			sentence = ' '.join(words)
			newSentence = ''
			for ch in sentence:
				if text:
					if ch == '<':
						text = False
					else:
						newSentence += ch 
				elif ch == '>':
					text = True

			if len(newSentence) > 0:
				print(' '.join(newSentence.split()))


####################### PREPROCESSING THE TXT FILE #######################
elif extension == 'txt':
	
	""" THE USER SHOULD DEFINE WHAT ANNOTATIONS THEY WANT TO PRESERVE HERE """
	labelMapping = {}
	# labelMapping['**'] = '$'
	labels = {}
	# labels['$'] = True
	# unfortunately raw text means we have to assume that consecutively marked words are the same named entity
	###########################################################################


	# THIS IS A HACKY WAY OF IGNORING SOME METADATA THAT LEAKED INTO THE RAW TEXT.. BUT IT CAN BE ADAPTED TO USERS' TEXTS OR SIMPLY COMMENTED OUT AND THE FOLLOWING BLOCK COMMENTED IN
	# body = False
	# for line in file:
	# 	go = False
	# 	line = line.split()
	# 	if len(line) > 0:
	# 		if body:
	# 			if len(line) != 2 or line[0] != 'page':
	# 				go = True
	# 		elif line[0].lower() == 'source:':
	# 			body = True

	### COMMENT THIS IN IF YOU HAVE NO META DATA TO IGNORE AS DEPICTED IN THE PRECEDING BLOCK
	for line in file:
		line = line.split()
		go = True

		if go:
			line = ' '.join(line)
			### REMOVE ALL ILLEGAL CHARACTERS AND THEN PUT IN THE LABELS
			for l in labels:
				line = line.replace(l,'')
			for l in labelMapping:
				line = line.replace(l,labelMapping[l])
			# line = line.replace('*','') # ANOTHER HACKY RELIC OF THE ANNOTATION
			line = line.split()

			### GO THROUGH EACH LINE AND MARK THE START AND END OF ALL NAMED ENTITIES
			for i in range(len(line)):
				for l in labels:
					if l in line[i][0:-1]:
						line[i] = l+' '+line[i].replace(l,'')
						end = i 
						for k in range(i+1,len(line)):
							if l in line[k]:
								line[k] = line[k].replace(l,'')
								end = k 
							else:
								break

						line[end] = line[end] + ' ' + l
						break

			print(' '.join(line))

else:
	print('ERROR: UNKNOWN FILE EXTENSION')
	sys.exit()


