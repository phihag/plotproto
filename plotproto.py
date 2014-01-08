#!/usr/bin/env python

from __future__ import unicode_literals

import argparse
import io
import json
import xml.etree.ElementTree


SubElement = xml.etree.ElementTree.SubElement

XFACTOR = 20
YFACTOR = 20
XMARGIN = 5
YMARGIN = 5
FONT_SIZE = 15
BITMARKER_HEIGHT = 10


def layout(fields, width):
    """
    Adds virtual_x1 / virtual_x2 and virtual_y1 / virtual_y2 (in virtual coordinates) to all fields
    Returns height in virtual coordinates
    """
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

    return field['virtual_y2']


def plot_file(fn):
    with io.open(fn, 'r', encoding='utf-8') as f:
        proto = json.load(f)

    doc = xml.etree.ElementTree.Element('svg')
    doc.attrib['xmlns'] = 'http://www.w3.org/2000/svg'

    width = proto.get('width', 32)
    large_mark_every = proto.get('large_mark_every', 8)
    medium_mark_every = proto.get('medium_mark_every', 4)

    fields = proto['fields']
    height = layout(fields, width)

    # Translate into physical coordinates
    document_width = XMARGIN + width * XFACTOR + XMARGIN
    document_height = YMARGIN + BITMARKER_HEIGHT + height * YFACTOR + YMARGIN

    xcoord = lambda v: XMARGIN + v * XFACTOR
    ycoord = lambda v: YMARGIN + BITMARKER_HEIGHT + YFACTOR * v
    doc.attrib['viewBox'] = '0 0 %d %d' % (document_width, document_height)

    bitmarkers = SubElement(doc, 'g')
    # Bit markers
    for i in range(0, width + 1):
        bm = SubElement(bitmarkers, 'line')
        factor = (
            1 if (i % large_mark_every) == 0 else
            (0.56 if (i % medium_mark_every) == 0 else 0.3)
        )
        bmheight = factor * BITMARKER_HEIGHT
        bm.attrib.update({
            'x1': str(xcoord(i)),
            'x2': str(xcoord(i)),
            'y1': str(ycoord(0) - bmheight),
            'y2': str(ycoord(0)),
            'style': 'stroke:#000000;stroke-opacity:1;stroke-width:1',
        })

    for field in fields:
        field['x1'] = xcoord(field['virtual_x1'])
        field['y1'] = ycoord(field['virtual_y1'])
        field['x2'] = xcoord(field['virtual_x2'])
        field['y2'] = ycoord(field['virtual_y2'])

        g = SubElement(doc, 'g')
        g.attrib['id'] = field['label']

        # Draw hint lines
        vheight = field['virtual_y2'] - field['virtual_y1']
        for i in range(1, vheight):
            line = SubElement(g, 'line')
            y = field['y1'] + i * YFACTOR
            line.attrib.update({
                'x1': str(field['x1']),
                'x2': str(field['x2']),
                'y1': str(y),
                'y2': str(y),
                'style': 'stroke:#000000;stroke-opacity:0.15;stroke-width:0.5',
            })

        t = SubElement(g, 'text')
        t.attrib.update({
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
