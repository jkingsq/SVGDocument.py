import xml.etree.ElementTree as ET

def clip(minimum, n, maximum):
    result = max(minimum, n)
    result = min(maximum, result)
    return result

def clipColor(color):
    r, g, b = color
    r = int(r)
    g = int(g)
    b = int(b)
    clip(0, r, 255)
    clip(0, g, 255)
    clip(0, b, 255)
    return (r, g, b)

def rgbToHex(color):
    return "#%02x%02x%02x" % clipColor(color)

class SVGDocument(ET.ElementTree):
    strokeColor = "#000000"
    strokeWidth = 1
    strokeOpacity = 1.0
    fillColor = "#ffffff"
    fillOpacity = 1.0
    def __init__(self, width=640, height=480, shapeRendering="auto"):
        attrib = {}
        attrib["xmlns"]="http://www.w3.org/2000/svg"
        attrib["width"] = str(int(width))
        attrib["height"] = str(int(height))
        attrib["shape-rendering"] = shapeRendering
        self.root = ET.Element("svg", attrib)
        super().__init__(self.root)

    def attribsTemplate(self):
        attribs = {}
        attribs["stroke"] = self.strokeColor
        attribs["stroke-width"] = self.strokeWidth
        attribs["stroke-opacity"] = self.strokeOpacity
        attribs["fill"] = self.fillColor
        attribs["fill-opacity"] = self.fillOpacity
        return attribs

    def addElement(self, tagName, attrib):
        for key in attrib:
            attrib[key] = str(attrib[key])
        ET.SubElement(self.getroot(), tagName, attrib)

    def setStrokeColor(self, r, g, b):
        """Set the stroke (outline) color to be used in objects subsequently added to
        the document
        """
        self.strokeColor = clipColor((r, g, b))

    def setStrokeWidth(self, width):
        """Set the stroke (outline) width to be used in objects subsequently added to
        the document
        """
        self.strokeWidth = float(width)

    def setStrokeOpacity(self, opacity):
        """Set the stroke (outline) opacity to be used in objects subsequently added
        to the document
        """
        self.strokeOpacity = float(clip(0.0, opacity, 1.0))

    def setFillColor(self, r, g, b):
        """Set the fill color to be used in objects subsequently added to the
        document
        """
        self.fillColor = rgbToHex((r, g, b))

    def addCircle(self, center, radius):
        """Add a circle to the document.
        Args:
            an (x, y) tuple representing the center
            the radius
        """
        attrib = self.attribsTemplate()
        cx, cy = center
        attrib["cx"] = cx
        attrib["cy"] = cy
        attrib["r"] = radius
        self.addElement("circle", attrib)

    def addPolygon(self, points, fillRule="evenodd"):
        """Add a polygon to the document.
        Args:
            an array of (x, y) tuples representing the vertices
            a string specifying which regions enclosed by the polygon are filled
        """
        attrib = self.attribsTemplate()
        attrib["points"] = ""
        for point in points:
            x, y = point
            attrib["points"] += "{},{} ".format(x, y)
        self.addElement("polygon", attrib)

        """Add a polyline to the document.
        Fill color and opacity WILL affect output and the image
        Args:
            an array of (x, y) tuples representing the vertices
        """
    def addPolyLine(self, points):
        attrib = self.attribsTemplate()
        for point in points:
            x, y = point
            x = float(x)
            y = float(y)
            attrib["points"] += "{},{} ".format(x, y)
        self.addElement("polyline", attrib)

    def addRect(self, topLeft, width, height, rx=0, ry=0):
        """Add a rectangle to the document.
        Args:
            an (x, y) tuple representing the top-left corner of the rectangle
            the width of the rectangle
            the height of the rectangle
            the width on each side over which corners are rounded
            the height on each side over which corners are rounded
        """
        attrib = self.attribsTemplate()
        x, y = topLeft
        attrib["x"] = x
        attrib["y"] = y
        attrib["rx"] = rx
        attrib["ry"] = ry
        attrib["width"] = width
        attrib["height"] = height
        self.addElement("rect", attrib)

    def addEllipse(self, center, rx, ry):
        """Add an ellipse to the document.
        Args:
          an (x, y) tuple representing the center of the ellipse
            the horizontal radius
            the vertical radius
        """
        attrib = self.attribsTemplate()
        x, y = center
        attrib["x"] = x
        attrib["y"] = y
        attrib["rx"] = rx
        attrib["ry"] = ry
        self.addElement("ellipse", attrib)

    def addLine(self, start, end):
        """Add a line to the document.
        Fill parameters are ignored and omitted in the document, since they would
        have no effect.
        Args:
            an (x, y) tuple representing the first endpoint of the line
            an (x, y) tuple representing the other endpoint of the line
        """
        attrib = self.attribsTemplate()
        del attrib["fill"]
        del attrib["fill-opacity"]
        x1, y1 = start
        x2, y2 = end
        attrib["x1"] = x1
        attrib["y1"] = y1
        attrib["x2"] = x2
        attrib["y2"] = y2
        self.addElement("line", attrib)
