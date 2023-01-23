import xml.etree.ElementTree as ET
from typing import Sequence, Tuple, Union

Number = Union[float, int]
Point = Tuple[Number, Number]

def clip(minimum, n, maximum):
    result = max(minimum, n)
    result = min(maximum, result)
    return result

def clipColor(color: Tuple[Number, Number, Number]):
    r, g, b = color
    r = int(r)
    g = int(g)
    b = int(b)
    clip(0, r, 255)
    clip(0, g, 255)
    clip(0, b, 255)
    return (r, g, b)

def rgbToHex(color: Tuple[Number, Number, Number]):
    return "#%02x%02x%02x" % clipColor(color)

class SVGPath:
    def __init__(self):
        # "movements" are of the form (char, [points])
        self.movements = []

    # make path string for a single SVGPath gesture
    def movementString(self, move: Tuple[str, Sequence[Number]]):
        gesture, points = move
        result = gesture
        # separate components of coordinates with commas
        pointsStr = map(lambda x : ",".join(map(str, list(x))), move[1])
        # separate coordinates with spaces
        result += " ".join(pointsStr)
        return result
        
    def getPathString(self):
        return " ".join(map(self.movementString, self.movements))

    def moveTo(self, point: Point):
        self.movements.append(("M", [point]))

    def moveRelative(self, point: Point):
        self.movements.append(("m", [point]))

    def lineTo(self, *points: Point):
        self.movements.append(("L", points))

    def lineRelative(self, *points: Point):
        self.movements.append(("l", points))

    def horizontalLineTo(self, *points: Point):
        self.movements.append(("H", points))

    def horizontalLineToRelative(self, *points: Point):
        self.movements.append(("h", points))

    def verticalLineTo(self, *points: Point):
        self.movements.append(("V", points))

    def verticalLineToRelative(self, *points: Point):
        self.movements.append(("v", points))

    # Cubic bezier point sequences repeat in the form:
    #   controlPointA, controlPointB, endPoint, ...
    def validateCubicPointSequence(self, *points: Point):
        assert(len(points) >= 3)
        assert(len(points) % 3 == 0)

    def cubicBezier(self, *points: Point):
        self.validateCubicPointSequence(*points)
        self.movements.append(("C", points))

    def cubicBezierRelative(self, *points: Point):
        self.validateCubicPointSequence(*points)
        self.movements.append(("c", points))

    # "Smooth", or shorthand cubic bezier point sequences infer the first
    # control point, so they repeat in the form:
    #   controlPointB, endPoint
    def validateSmoothCubicPointSequence(self, *points: Point):
        assert(len(points) >= 2)
        assert(len(points) % 2 == 0)
        if not self.movements[-1][0] in {"C", "c", "S", "s"}:
            raise(Exception("smooth cubic curveto must be preceded by a cubic curve"))

    def smoothCubicBezier(self, *points: Point):
        self.validateSmoothCubicPointSequence(*points)
        self.movements.append(("S", points))

    def smoothCubicBezierRelative(self, *points: Point):
        self.validateSmoothCubicPointSequence(*points)
        self.movements.append(("s", points))

    # Quadratic bezier point sequences repeat in the form:
    #   controlPoint, endPoint, ...
    def validateQuadraticPointSequence(self, *points: Point):
        assert(len(points) >= 2)
        assert(len(points) % 2 == 0)

    def quadraticBezier(self, *points: Point):
        self.validateQuadraticPointSequence(*points)
        self.movements.append(("Q", points))

    def quadraticBezierRelative(self, *points: Point):
        self.validateQuadraticPointSequence(*points)
        self.movements.append(("q", points))

    # "Smooth", or shorthand quadratic bezier point sequences infer the control
    # points, so only the points on the line are provided.
    def validateSmoothQuadraticPointSequence(self, *points: Point):
        assert(len(points) >= 1)
        if not self.movements[-1][0] in {"Q", "q", "T", "t"}:
            raise(Exception("smooth quadratic curveto must be preceded by a quadratic curve"))

    def smoothQuadraticBezier(self, *points: Point):
        self.validateSmoothQuadraticPointSequence(points)
        self.movements.append(("T", points))

    def smoothQuadraticBezierRelative(self, *points: Point):
        self.validateSmoothQuadraticPointSequence(points)
        self.movements.append(("t", points))

    def elipticalArcTo(self, \
            radiusX: Number, \
            radiusY: Number, \
            rotation: Number,
            largeArc: bool, \
            sweep: bool, \
            point: Point):
        arcFlags = (int(largeArc), int(sweep))
        self.movements.append(("A", [(radiusX, radiusY), rotation, arcFlags, point]))

    def closePath(self):
        self.movements.append(("Z", []))

class SVGDocument(ET.ElementTree):
    strokeColor = "#000000"
    strokeWidth = 1
    strokeOpacity = 1.0
    fillColor = "#ffffff"
    fillOpacity = 1.0
    fillRule = "evenodd"
    def __init__(self, width: Number, height: Number, shapeRendering="auto"):
        attrib = {}
        attrib["xmlns"]="http://www.w3.org/2000/svg"
        attrib["width"] = str(int(width))
        attrib["height"] = str(int(height))
        attrib["shape-rendering"] = shapeRendering
        self.root = ET.Element("svg", attrib)
        super().__init__(self.root)

    def attribsTemplate(self, stroke=True, fill=True):
        attribs = {}
        if not stroke or self.strokeOpacity == 0:
            attribs["stroke"] = "none"
        else:
            attribs["stroke"] = self.strokeColor
            attribs["stroke-width"] = self.strokeWidth
            attribs["stroke-opacity"] = self.strokeOpacity
        if not fill or self.fillOpacity == 0:
            attribs["fill"] = "none"
        else:
            attribs["fill"] = self.fillColor
            attribs["fill-opacity"] = self.fillOpacity
            attribs["fill-rule"] = self.fillRule
        return attribs

    # Not recommended for use outside this module
    def addElement(self, tagName, attrib):
        for key in attrib:
            attrib[key] = str(attrib[key])
        ET.SubElement(self.getroot(), tagName, attrib)

    def setStrokeColor(self, r: Number, g: Number, b: Number):
        """Set the stroke (outline) color to be used in objects subsequently added to
        the document
        """
        self.strokeColor = rgbToHex((r, g, b))

    def setStrokeWidth(self, width: Number):
        """Set the stroke (outline) width to be used in objects subsequently added to
        the document
        """
        self.strokeWidth = width

    def setStrokeOpacity(self, opacity: Number):
        """Set the stroke (outline) opacity to be used in objects subsequently added
        to the document
        """
        self.strokeOpacity = clip(0.0, opacity, 1.0)

    def setFillColor(self, r: Number, g: Number, b: Number):
        """Set the fill color to be used in objects subsequently added to the
        document
        """
        self.fillColor = rgbToHex((r, g, b))

    def setFillOpacity(self, opacity: Number):
        """Set the fill opacity to be used in objects subsequently added to the
        document
        """
        self.fillOpacity = clip(0.0, opacity, 1.0)

    def setFillEvenOdd(self):
        self.fillRule = "evenodd"

    def setFillNonZero(self):
        self.fillRule = "nonzero"

    def addCircle(self, center: Point, radius: Number):
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

    def addPolygon(self, *points: Point):
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

    def addPolyLine(self, *points: Point):
        """Add a polyline to the document.
        Fill color and opacity WILL affect output and the image
        Args:
            an array of (x, y) tuples representing the vertices
        """
        attrib = self.attribsTemplate()
        attrib["points"] = ""
        for point in points:
            x, y = point
            attrib["points"] += "{},{} ".format(x, y)
        self.addElement("polyline", attrib)

    def addRect(self, topLeft: Point, width: Number, height: Number, rx=0, ry=0):
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

    def addEllipse(self, center: Point, rx: Number, ry: Number):
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

    def addLine(self, start: Point, end: Point):
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

    def addSVGPath(self, path: SVGPath, stroke=True, fill=True):
        attrib = self.attribsTemplate(stroke, fill)
        attrib["d"] = path.getPathString()
        self.addElement("path", attrib)
