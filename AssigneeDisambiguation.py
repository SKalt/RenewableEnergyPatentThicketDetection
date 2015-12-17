# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 20:48:03 2015
Assignee Disambiguator FINAL
@author: steven

This program (1) generates a list of common corporation suffixes and
(2) disambiguates the raw assignment data provided by the USPTO, as processed
by the Harvard Patent Dataverse.  
"""

import pandas as pd
import string
#%% Part 1: generating common corporation suffixes
# load cleantech patent dataframe, then pare it down to assignment and patent
# number data
# this data is also available at 
# http://funglab.berkeley.edu/guanchengli/cleantech_patents.tsv

cleantech = pd.read_csv('/home/steven/Downloads/cleantech_patents.tsv',
                        header = None, 
                        sep = '\t')
#%%
# make an all-upper-case list of cleantech assignees
cleanAssignees = list(cleantech[1]) # 7007 patents 
cleanAssignees = [str(x).upper() for x in cleanAssignees] 
cleanPatents = cleantech[0]

#%%
uniqueAssignees = list(set([i for i in cleanAssignees if type(i) == str]))#7229
assigneesLeft = uniqueAssignees
#%%
words = []
for i in uniqueAssignees:
    if type(i) == str:
        words += i.split()
#%%   
words2 = pd.Series(words)
wordCount = words2.value_counts()
#%%
# measure how many unique company names are left after removing each of the
# unique words, then each of the less unique words
print(len(assigneesLeft))

for i in range(1,11):
    classifiers = wordCount[wordCount == i]
    for x in assigneesLeft:
        for y in classifiers.index:
            if y in x: 
                try:
                    assigneesLeft.remove(x)
                except:
                    pass
    print(len(assigneesLeft))
#7229
#3674
#1850
#1311
#1150
#729
#387
#312
#294
#277
#268

#%%
# a hand-picked list of the most common corporation suffixes, generated from 
# wordCount
corpisms = ['Inc.', 'Inc.,', 'Inc',
            'Corporation', 'Corporation,', 'Corporation)',
            'Co.', 'Co.,', 'Co',
            'Corp.', 'Corp.,', 'Corp ',
            'Company', 'Company,', 'Compny',
            'Incorporated', 'Incorporation',
            'P.C.', 'P.L.C.', 'PLC.',
            'Kabushiki', 'Kabushika', 'Kabuhsiki',
            'S.A.', 'S.A.,',
            'a.s.','A/S', 'A/S,', 'AS',
            'S.p.A.', 'S.p.A..', 'S.P.A.',
            'LLP', 'LLP.', 'LP',
            'Ltd.', 'Ltda.', 'Ltd.,',
            'LLC', 'PLLC', 'LLC.',
            'GmbH', 'GmbH.', 'mbH',
            'University', 'Universtiy', 'Universite',
            'Limited', 'Limited,', 'limited',
            'Pty', 'Pty.', 'Pty.,',
            'International', 'Internationale', 'International,'
            'AG','AB','SL']
# remove all of  the punctuation and case differences from each of the corpisms
puncRemover = ''.maketrans('','', string.punctuation)
corpisms2 = list(set([x.translate(puncRemover).upper() for x in corpisms]))

#%%
# remove all the case differences and punctuation from uniqueAssignees, then
# split each company name into a list of words
 
uniqueAssignees2 = [i.upper() for i in uniqueAssignees]
uniqueAssignees2 = [i.translate(puncRemover) for i in uniqueAssignees2]
uniqueAssignees2 = [i.split() for i in uniqueAssignees2]
#%%
# create a list of company names without any of the company identifiers
# this assumes there is no difference beween companies with different suffixes
# like 'Energy, Inc.' and 'Energy Corp.'
uniqueAssignees3 = [
[x for x in comp if x not in corpisms2]
 for comp in uniqueAssignees2]
uniqueAssignees4  = [' '.join(x) for x in uniqueAssignees3]
print(len(uniqueAssignees4)) #7229
print(len(set(uniqueAssignees4))) #6475
#%% Part 2: disambiguation of the Harvard Patent Dataverse assignee data


#%%
# load in raw assignee data
assignee = pd.read_csv('/home/steven/Downloads/assignee.csv')
#%%
# pare raw assignee data down to the Series with assignee names
origAssignees0 = assignee['Assignee']
print(len(origAssignees0))
origAssignees = origAssignees0[pd.notnull(origAssignees0)]
len(set(list(origAssignees))) # 412984, 0.10 of the number of assignments
#%%
# now the real deal, disambiguation on the full clean assignment df
origAssignees2 = [i.translate(puncRemover).upper() 
    for i in origAssignees
    if type(i) == str]
len(set(origAssignees2)) # 339191 # .821 of the original unique comp names
#%%
origAssignees3 = [i.split() for i in origAssignees2]
origAssignees4 = [
[x for x in comp if x not in corpisms2]
for comp in origAssignees3
]
origAssignees5 = [' '.join(i) for i in origAssignees4]
#%%
len(set(origAssignees5)) # 309412 # .749 of the original set
#%% 
# prepare raw patent numbers for merging with cleantech patent numbers
# needs to be re-merged with df
patents = assignee['Patent']
patents = patents[pd.notnull(patents)]
patents2 = [ 
x[1::] if len(str(x)) == 8 and str(x)[0] == '0'
else x 
for x in patents
] # 4016128, 3950972 unique  => ~2% multiple assignment
# I'm juuuust going to ignore that. 
#%%
#re-merge modified data into the df
assignee.loc[pd.notnull(assignee['Assignee']),'Assignee'] = origAssignees5
assignee.loc[:,'Patent'] = patents2
#%%
# save the assignee df as a new tsv
assignee.to_csv('/home/steven/Downloads/assignee2.tsv', sep = '\t', 
                encoding = 'utf-8')