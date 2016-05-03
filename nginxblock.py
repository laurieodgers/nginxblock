# The MIT License (MIT)
# Copyright (c) 2016 Laurence Odgers
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files 
# (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from collections import defaultdict
from collections import OrderedDict
import re
import json


class NginxBlock:
    name = None
    value = None
    attrs = None
    blocks = None

    # constructor
    def __init__(self):
        # set attrs and blocks as 2d dicts
        self.attrs = defaultdict(dict)
        self.blocks = defaultdict(dict)
    
    # allow attrs and blocks to be addressable without having to use their relevant dict names
    def __getattr__(self, key):
        # look for attrs first
        if (key in self.attrs):
            return self.attrs[key]
        # and now blocks
        elif (key in self.blocks):
            return self.blocks[key]
        
    # opens a file and parses it recursively 
    def openFile(self, filePath):
        # sanity check
        if (len(filePath) == 0):
            return False
        
        # open file
        f = open(filePath, 'r')
        
        # parse it
        self.parse(f.read(), 0)
    
    # saves the output of toString to file
    def saveFile(self, filePath):
        # sanity check
        if (len(filePath) == 0):
            return False
        
        # open file
        f = open(filePath, 'w')
        
        # save the data
        return f.write(self.toString())
    
    # adds an attribute
    def addAttr(self, name, value):
        # sanity checks
        if (len(name) == 0):
            return False
        
        # use a number as a key
        index = len(self.attrs[name])

        if (len(value) > 0):
            self.attrs[name][index] = value
        else:
            self.attrs[name][index] = None
            
        return True
    
    # adds a block
    def addBlock(self, name, value, block):
        # sanity checks
        if (len(name) == 0):
            return False
        
        if (block is None):
            return False
        
        # check if a value was set
        if (len(value) > 0):
            # use the value as a key
            self.blocks[name][value] = block
            
        else:
            # use a number as a key
            index = len(self.blocks[name])
            # add the block
            self.blocks[name][index] = block
    
    # converts this object to JSON
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    # converts this object back into a config file
    def toString(self, depth = 0):
        # set the required indent for this level
        blockIndent = 4 * depth
        attrIndent = 4 * depth
        
        # sort the attrs and blocks by key for predictable output
        sortedAttrs = OrderedDict(sorted(self.attrs.items(), key=lambda t: t[0]))
        sortedBlocks = OrderedDict(sorted(self.blocks.items(), key=lambda t: t[0]))

        string = ''
        # print the name if set
        if (self.name is not None):
            line = self.name + " "
            # add the value if its present
            if (self.value is not None):
                line = line + self.value + " "
        
            string = string + line.rjust(blockIndent + len(line)) + "{\n"
            attrIndent += 4
        else:
            # no name (root object), decrement the depth for better formatting
            depth -= 1
        
        # print attrs
        for row in sortedAttrs:
            for val in sortedAttrs[row]:
                # format the line first
                line = row + " " + sortedAttrs[row][val]
                # add it to our string
                string = string + line.rjust(attrIndent + len(line)) + ";\n"
        
        # print blocks
        for row in sortedBlocks:
            for val in sortedBlocks[row]:
                # recursively print out the blocks
                string = string + sortedBlocks[row][val].toString(depth + 1) + "\n"

        # append a final curly brace if a name was set
        if (self.name is not None):
            string = string + "}".rjust(blockIndent + 1)

        return string

    # parses an nginx config file recursively
    def parse(self, string, depth = 0):
        # set some variables for this run
        numBlocks = 0
        thisBlock = ''
        blockName = ''
        blockValue = ''
        
        # loop over the lines
        for line in string.splitlines():
            # clean up the line
            # remove any comments
            line = line.split('#', 1)[0]
            # clean up whitespace
            line = line.strip()
            
            # check for close curly brace
            if (re.match('^}$', line) is not None):
                numBlocks -= 1

            # matches first block in the string
            if (numBlocks == 0) and (re.match('^.+{$', line) is not None):
                # strip off the curly brace
                tmp = line.rstrip('{')
                tmp = tmp.strip()
                
                # check if its a key or a key value pair
                if (re.search(r"\s", tmp)): 
                    # key value
                    blockName = tmp.split(' ', 1)[0].strip()
                    blockValue = tmp.split(' ', 1)[1].strip()
                else:
                    # key only
                    blockName = line.split(' ')[0].strip()

            # add to our block if it wasnt the start block or end block
            if (numBlocks > 0) and (len(line) > 0):
                thisBlock += line + "\n"
            
            # start of a block
            if (re.match('^.+{$', line) is not None):
                numBlocks += 1
            
            # matches key values/attrs for this object
            if (re.match('^\w.+\s.+\w.+$', line) is not None) and (numBlocks == 0):
                # clean up the string
                line = line.rstrip(';')
                line = line.strip()
                
                # squash spaces
                line = re.sub( '\s+', ' ', line)
                
                # add it
                self.addAttr(line.split(' ', 1)[0].strip(), line.split(' ', 1)[1].strip())
            
            # if this is a closing curly brace and we're at level 0 then form the object
            if (re.match('^}$', line) is not None) and (numBlocks == 0):
                # create a new block and set its name and value
                block = NginxBlock()
                
                # set its name and value
                block.name = blockName
                if (len(blockValue) > 0):
                    block.value = blockValue
                
                # parse this block
                block.parse(thisBlock, (depth + 1))
                
                # add it to our 2d dict
                self.addBlock(blockName, blockValue, block)
                
                # reset values and continue processing
                thisBlock=''
                blockName = ''
                blockValue = ''
