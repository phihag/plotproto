#!/usr/bin/env python

import io
import json
import argparse
import xml.etree.ElementTree


SubElement = xml.etree.ElementTree.SubElement


def plot_file(fn, width=32):
    with io.open(fn, 'r', encoding='utf-8') as f:
        proto = json.load(f)

    doc = xml.etree.ElementTree.Element('svg')
    doc.attrib['xmlns'] = 'http://www.w3.org/2000/svg'

    x = 0
    y = 0
    for field in proto['fields']:
        size = field['size']
        assert (x + size <= width) or (x == 0 and size % width == 0)
        t = SubElement(doc, 'text')
        t.text = field['label']

    xml.etree.ElementTree.dump(doc)


def main():
    parser = argparse.ArgumentParser(description='Plot protocol formats')
    parser.add_argument(
        'file', metavar='FILE', help='Protocol description file')
    opts = parser.parse_args()
    
    plot_file(opts.file)

if __name__ == '__main__':
    main()
