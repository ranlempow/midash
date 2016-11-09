import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('../midash'))



testVectors = [
    ["EmptyObject", '{}', {}],
    ["EmptyArray", '[]', []],
    ["EmptyObjectInList", '[{}]', [{}]],
    ["ObjectWithEmptyList", '{"test": [] }', {"test": [] }],
    ["ObjectWithEmptyKey", '{"": "" }', {"": "" }],
    ["ObjectWithNonEmptyList", '{"test": [3, 4, 5] }', {"test": [3, 4, 5] }],
    ["True", 'true', True],
    ["False", 'false', False],
    ["Null", 'null', None],
    ["SmallObject", '{ "name" : "Patrick", "age" : 44}', { "age" : 44, "name" : "Patrick"}],
    ["EmptyObjectAtEndOfArray", '["a","b","c",{}]', ["a","b","c",{}]],
    ["EmptyObjectMidArray", '["a","b",{},"c"]', ["a","b",{},"c"]],
    ["ClosingObjectBracket", '{"a":[1,2,3]}', {"a":[1,2,3]}],
    ["SmallArray1", '["a", "b", "c"]', ["a", "b", "c"]],
    ["SmallArray2", '[1, 2, 3, 4]', [1, 2, 3, 4]],
    ["ArrayOfSymbols", '[true, false, null]', [True, False, None]],
    ["StringValue", '{ "name" : "Patrick" }', { "name" : "Patrick" }],
    ["IntegerValue", '{ "age" : 44 }', { "age" : 44 }],
    ["LongValue", '12345678901234567890', 12345678901234567890],
    ["NegativeIntegerValue", '{ "key" : -44 }', { "key" : -44 }],
    ["FloatValue1", '3.44556677', 3.44556677],
    ["FloatValue2", '{ "age" : 44.5 }', { "age" : 44.5 }],
    ["NegativeFloatValue", '{ "key" : -44.5 }', { "key" : -44.5 }],
    ["EscapedQuotationMark", r'"\""', '"'],
    ["Solidus", r'"/"', '/'],
    ["EscapedReverseSolidus", r'"\"', '\\'],
    ["EscapedBackspace", r'"\b"', '\b'],
    ["EscapedFormfeed", r'"\f"', '\f'],
    ["EscapedNewline", r'"\n"', '\n'],
    ["EscapedCarriageReturn", r'"\r"', '\r'],
    ["EscapedHorizontalTab", r'"\t"', '\t'],
    ["EscapedEscapedHexCharacter1", r'"\u000A"', '\n'],
    ["EscapedEscapedHexCharacter2", r'"\u1001"', '\u1001'],
]

compact = [{"Female?":False,"age":44,"name":"Patrick","grandchildren":None,"Employed?":True},"used","abused","confused",1,2,[3,4,5]]
compact_str = '[{"Female?":false,"age":44,"name":"Patrick","grandchildren":null,"Employed?":true},"used","abused","confused",1,2,[3,4,5]]'
multiline_str = '''
[
    { "name": "Patrick", "age" : 44,
      "Employed?" : true, "Female?" : false,
      "grandchildren":null },
    "used",
    "abused",
    "confused",
    1,
    2,
    [3, 4, 5]
]
'''

testLoadsVectors = [
    ["ComplexArray", compact_str, compact],
    ["ComplexArray", multiline_str, compact],
]

exceptErrorVectors = [
    ["ReadBadObjectKey", '{ 44 : "age" }', Exception],
    ["ReadBadArray", '[1,2,3,,]', Exception],
    ["BadObjectSyntax", '{"age", 44}', Exception],
    ["ReadBadNumber", '-44.4.4', Exception],
    ["IncompleteArray1", '[', Exception],
    ["IncompleteArray2", '[1,2,3', Exception],
    ["IncompleteArray3", '[1,2,3,', Exception],
    ["ReadBadEscapedHexCharacte", r'"\u10K5"', Exception],
]




import jsonlua

def _removeWhitespace(str):
    return str.replace(" ", "")


class JsonTest(unittest.TestCase):
    def testWrite(self):
        for name, string, obj in testVectors:
            print("test reading... " + name)
            data = jsonlua.dumps(obj)
            self.assertEqual(_removeWhitespace(string), _removeWhitespace(data))
    
    def testRead(self):
        for name, string, obj in (testVectors + testLoadsVectors):
            print("test writing... " + name)
            loaded = jsonlua.loads(string)
            self.assertEqual(obj, loaded)
            
    def testException(self):
        for name, string, exp in exceptErrorVectors:
            print("test exception... " + name)
            self.assertRaises(exp, lambda: jsonlua.loads(string))

        
def main():
    unittest.main()

if __name__ == '__main__':
    main()
