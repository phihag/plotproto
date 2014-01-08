#!/usr/bin/env python

from __future__ import unicode_literals

import functools
import io
import json
import argparse
import sys
import xml.etree.ElementTree


SubElement = xml.etree.ElementTree.SubElement

XFACTOR = 20
YFACTOR = 20
XMARGIN = 5
YMARGIN = 5
FONT_SIZE = 15


def layout(fields, width=None):
    """
    Adds x1 / x2 and y1 / y2 (in SVG coordinates) to all fields
    Returns (width, height) in SVG coordinates
    """

    if width is None:
        width = 32

    # Calculate virtual coordinates
    x = 0
    y = 0
    for field in fields:
        size = field['size']
        assert size >= 1
        assert (x + size <= width) or (x == 0 and size % width == 0)

        field['virtual_x1'] = x
        field['virtual_y1'] = y
        field['virtual_x2'] = x + ((size - 1) % width) + 1
        field['virtual_y2'] = y + max(size // width, 1)

        y = y + ((x + size) // width)
        x = (x + size) % width

    last_y = field['virtual_y2']

    # Translate into physical coordinates
    document_width = XMARGIN + width * XFACTOR + XMARGIN
    document_height = YMARGIN + last_y * YFACTOR + YMARGIN

    xcoord = lambda v: XMARGIN + v * XFACTOR
    ycoord = lambda v: document_height - YMARGIN - YFACTOR * v
    for f in fields:
        f['x1'] = xcoord(f['virtual_x1'])
        f['y1'] = xcoord(f['virtual_y1'])
        f['x2'] = xcoord(f['virtual_x2'])
        f['y2'] = xcoord(f['virtual_y2'])

    return (document_width, document_height)


def plot_file(fn, width=None):
    with io.open(fn, 'r', encoding='utf-8') as f:
        proto = json.load(f)

    doc = xml.etree.ElementTree.Element('svg')
    doc.attrib['xmlns'] = 'http://www.w3.org/2000/svg'

    fields = proto['fields']
    layout(fields)

    for field in proto['fields']:
        g = SubElement(doc, 'g')
        g.attrib['id'] = field['label']

        t = SubElement(g, 'text')
        t.attrib.update({
            # TODO look at font size
            'x': str((field['x1'] + field['x2']) / 2),
            'y': str((field['y1'] + field['y2']) / 2),
            'text-anchor': 'middle',
            'dy': '%s' % (.3 * FONT_SIZE),
            'font-size': '%s' % FONT_SIZE,
        })
        t.text = field['label']
        r = SubElement(g, 'rect')
        r.attrib.update({
            'x': str(field['x1']),
            'y': str(field['y1']),
            'width': str(abs(field['x2'] - field['x1'])),
            'height': str(abs(field['y2'] - field['y1'])),
            'style': 'fill:none;stroke:#000000;stroke-opacity:1',
        })

    xml.etree.ElementTree.dump(doc)


def main():
    parser = argparse.ArgumentParser(description='Plot protocol formats')
    parser.add_argument(
        'file', metavar='FILE', help='Protocol description file')
    opts = parser.parse_args()
    
    plot_file(opts.file)

if __name__ == '__main__':
    main()
