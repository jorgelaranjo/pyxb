"""Classes corresponding to W3C XML Schema components.

Class names and behavior should conform to the schema components
described in http://www.w3.org/TR/xmlschema-1/.

Each class has a CreateFromDOM class method that creates an instance
and initializes it from a DOM node.

Classes that need to support built-ins also support a
CreateBaseInstance class method that creates a new instance manually.

"""

from PyWXSB.exceptions_ import *
from xml.dom import Node
import types
import PyWXSB.Namespace as Namespace

class PythonSimpleTypeSupport(object):
    """Class to support converting between WXS simple types and Python
    native types.

    There must be a one-to-one correspondence between instances of (a
    subclass of) this class and any built-in simple types except
    lists (and unions).

    Schema-defined STDs do not currently provide a mechanism to
    associate a PST.  Instead:

    * Absent types (e.g., restrictions of the ur type) and Atomic
      types use the PST of their base type definition (recursively,
      until a PST is found).
    * Lists use the PST of their item type definition.
    * Unions use the PSTs of their member type definitions.

    Currently, the only built-in non-atomic STDs are list variety, and
    they should use the PST of the underlying itemTypeDefinition just
    as schema-defined STDs do.

    @note This is a new-style class, involved in a complex inheritance
    hierarchy.  If you descend from it and define a custom __init__
    method, it must use only keyword arguments and invoke
    super.__init__(**kw).  Positoinal arguments are explicitly
    disallowed.

    """
    
    # A reference to the XMLSchema.structures.SimpleTypeDefinition
    # instance for which this instance provides support.  The
    # reference is bidirectional through the other side's
    # __pythonSupport variable.  It may be assigned only once, and is
    # done when this instance is bound to an STD.
    __simpleTypeDefinition = None

    # A value reflecting the Python type into which this XML type is
    # converted.  SHould be overridden in child classes.  A value of
    # None indicates that no suitable Python type can be presumed.
    PythonType = None

    @classmethod
    def SuperType (cls):
        """Identify the immediately higher class in the
        PythonSimpleTypeSupport hierarchy.

        The topmost class in the hierarchy considers itself to be its
        own SuperType."""
        if PythonSimpleTypeSupport == cls:
            return cls
        for sc in cls.__bases__:
            if issubclass(sc, PythonSimpleTypeSupport):
                return sc
        raise LogicError('%s: Unable to identify superType' % (cls.__name__,))

    def _setSimpleTypeDefinition (self, std):
        """Set the simple type definition corresponding to this PSTS.

        This method should only be invoked by SimpleTypeDefinition."""
        if self.__simpleTypeDefinition:
            raise LogicError('Multiple assignments of SimpleTypeDefinition to PythonSTSupport')
        self.__simpleTypeDefinition = std
        return self

    def simpleTypeDefinition (self):
        """Return a reference to the SimpleTypeDefinition component
        bound to this type."""
        assert self.__simpleTypeDefinition is not None
        return self.__simpleTypeDefinition

    # Even when we have an instance of a simple type definition, we do
    # the conversion routines as class methods, so they can be used
    # explicitly.

    def stringToPython (self, value):
        """Convert a value in string form to a native Python data value.

        This method invokes the class method for this instance.  It is
        invoked as a pass-thru by SimpleTypeDefinition.stringToPython.

p        @throw PyWXSB.BadTypeValueError if the value is not
        appropriate for the simple type.
        """
        return self.__class__.StringToPython(value)
        
    def pythonToString (self, value):
        """Convert a value in native Python to a string appropriate for the simple type.

        This method invokes the corresponding class method.  It is
        invoked as a pass-thru by SimpleTypeDefinition.pythonToString
        """
        return self.__class__.PythonToString(value)

    @classmethod
    def StringToPython (cls, value):
        """Convert a value in string form to a native Python data value.

        This method should be overridden in primitive PSTSs.

        @throw PyWXSB.BadTypeValueError if the value is not
        appropriate for the simple type.
        """
        raise IncompleteImplementationError('%s: Support does not define stringToPython' % (cls.__simpleTypeDefinition.name(),))
        
    @classmethod
    def PythonToString (cls, value):
        """Convert a value in native Python to a string appropriate for the simple type.

        This method should be overridden in primitive PSTSs.
        """
        raise IncompleteImplementationError('%s: Support does not define pythonToString' % (cls.__simpleTypeDefinition.name(),))

    @classmethod
    def StringToList (cls, values, item_type_definition):
        """Extract a list of values of the given type from a string.

        This is used for an STD with variety 'list'.
        @todo Implement StringToList
        """
        raise IncompleteImplementationError('PythonSimpleTypeSupport.stringToList')

    @classmethod
    def ListToString (cls, values, item_type_definition):
        """Encode a sequence of values of the given type as a string

        This is used for an STD with variety 'list'.
        @todo Implement ListToString"""
        raise IncompleteImplementationError('PythonSimpleTypeSupport.StringToList')

    @classmethod
    def StringToUnion (cls, values, member_type_definitions):
        """Extract a value of one of the given types from a string.

        This is used for an STD with variety 'union'.
        @todo Implement StringToUnion"""
        raise IncompleteImplementationError('PythonSimpleTypeSupport.stringToUnion')

    @classmethod
    def UnionToString (cls, values, member_type_definitions):
        """Encode a value as a string.

        This is used for an STD with variety 'union'.
        @todo Implement UnionToString"""
        raise IncompleteImplementationError('PythonSimpleTypeSupport.StringToUnion')

# Datatypes refers to PythonSimpleTypeSupport, so the import must
# follow its declaration.
import datatypes

def LocateUniqueChild (node, schema, tag, absent_ok=True):
    candidate = None
    # @todo identify QName children as well as NCName
    name = schema.xsQualifiedName(tag)
    for cn in node.childNodes:
        if cn.nodeName == name:
            if candidate:
                raise SchemaValidationError('Multiple %s elements nested in %s' % (name, node.nodeName))
            candidate = cn
    if (candidate is None) and not absent_ok:
        raise SchemaValidationError('Expected %s elements nested in %s' % (name, node.nodeName))
    return candidate

def LocateFirstChildElement (node, absent_ok=True, require_unique=False):
    candidate = None
    for cn in node.childNodes:
        if Node.ELEMENT_NODE == cn.nodeType:
            if require_unique:
                if candidate:
                    raise SchemaValidationError('Multiple elements nested in %s' % (node.nodeName,))
                candidate = cn
            else:
                return cn
    if (candidate is None) and not absent_ok:
        raise SchemaValidationError('No elements nested in %s' % (node.nodeName,))
    return candidate

def HasNonAnnotationChild (wxs, node):
    xs_annotation = wxs.xsQualifiedNames('annotation')
    for cn in node.childNodes:
        if Node.ELEMENT_NODE != cn.nodeType:
            continue
        if cn.nodeName not in xs_annotation:
            return True
    return False

class _NamedComponent_mixin:
    """Mix-in to hold the name and target namespace of a component.

    The name may be None, indicating an anonymous component."""
    # Value of the component.  None if the component is anonymous.
    __name = None

    # None, or a reference to a Namespace in which the component may be found
    # @todo Figure out how to stripProxies from this when unpickling.
    __targetNamespace = None
    
    # The schema in which qualified names for the namespace should be
    # determined.
    __schema = None

    def __init__ (self, name, target_namespace):
        assert (name is None) or (0 > name.find(':'))
        self.__name = name
        if target_namespace is not None:
            self.__targetNamespace = target_namespace.stripProxies()
        self.__schema = None
            
    def targetNamespace (self):
        """Return the namespace in which the component is located."""
        return self.__targetNamespace

    def ncName (self):
        """Return the local name of the component."""
        return self.__name

    def name (self):
        """Return the QName of the component."""
        if self.__targetNamespace is not None:
            if self.__name is not None:
                return '%s[%s]' % (self.__name, self.__targetNamespace.uri())
            return '#??[%s]' % (self.__targetNamespace.uri(),)
        return self.__name

    def isNameEquivalent (self, other):
        """Return true iff this and the other component share the same name and target namespace.
        
        Anonymous components are inherently name inequivalent."""
        # Note that unpickled objects 
        return (self.__name is not None) and (self.__name == other.__name) and (self.__targetNamespace.equals(other.__targetNamespace))

class _Resolvable_mixin:
    """Mix-in indicating that this component may have references to unseen named components."""
    def __init__ (self):
        pass
    
    def isResolved (self):
        """Determine whether this named component is resolved.

        Override this in the child class."""
        raise LogicError('Resolved check not implemented in %s' % (self.__class__,))
    
    def _resolve (self, wxs):
        """Perform whatever steps are required to resolve this component.

        Resolution is performed in the context of the provided schema.
        Invoking this method may fail to complete the resolution
        process if the component itself depends on unresolved
        components.  The sole caller of this should be
        schema._resolveDefinitions().
        
        Override this in the child class.  The method should return
        self.  In the prefix, if isResolved() is true, return right
        away.  If something prevents you from completing resolution,
        invoke wxs._queueForResolution(self) so it is retried later,
        then immediately return self.  Prior to leaving after
        successful resolution discard any cached dom node by setting
        self.__domNode=None.

        """
        raise LogicError('Resolution not implemented in %s' % (self.__class__,))
        

class AttributeDeclaration (_NamedComponent_mixin, _Resolvable_mixin):
    VC_na = 0                   #<<< No value constraint applies
    VC_default = 1              #<<< Provided value constraint is default value
    VC_fixed = 2                #<<< Provided value constraint is fixed value

    __typeDefinition = None
    def typeDefinition (self): return self.__typeDefinition

    SCOPE_global = 'global'
    xSCOPE_unhandled = 'unhandled'
    # None, the string "global", or a reference to a _ComplexTypeDefinition
    __scope = None
    def scope (self): return self.__scope

    # None, or a tuple containing a string followed by one of the VC_*
    # values above.
    __valueConstraint = None
    def valueConstraint (self): return self.__valueConstraint

    __annotation = None

    def __init__ (self, name, target_namespace):
        _NamedComponent_mixin.__init__(self, name, target_namespace)
        _Resolvable_mixin.__init__(self)

    @classmethod
    def CreateBaseInstance (cls, name, target_namespace=None):
        bi = cls(name, target_namespace)
        return bi

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        # Node should be an XMLSchema attribute node
        assert node.nodeName in wxs.xsQualifiedNames('attribute')

        name = None
        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')
            namespace = wxs.getTargetNamespace()
        elif not node.hasAttribute('ref'):
            namespace = wxs.getTargetNamespaceFromDOM(node, 'attributeFormDefault')

        rv = cls(name, namespace)

        rv.__domNode = node
        wxs._queueForResolution(rv)
        return rv

    def isResolved (self):
        return self.__typeDefinition is not None

    def _resolve (self, wxs):
        if self.isResolved():
            return self
        #print 'Resolving AD %s' % (self.name(),)
        node = self.__domNode

        # Implement per section 3.2.2
        if node.parentNode.nodeName in wxs.xsQualifiedNames('schema'):
            self.__scope = self.SCOPE_global

        elif not node.hasAttribute('ref'):
            # The AttributeUse component is resolved elsewhere
            # @todo Set scope to enclosing complexType, if present
            self.__scope = self.xSCOPE_unhandled
        else:
            # I think this is really a schema validation error
            raise IncompleteImplementationError('Internal attribute declaration by reference')
        
        st_node = LocateUniqueChild(node, wxs, 'simpleType')
        if st_node is not None:
            self.__typeDefinition = SimpleTypeDefinition.CreateFromDOM(wxs, st_node)
        elif node.hasAttribute('type'):
            # Although the type definition may not be resolved, *this* component
            # is resolved, since we don't look into the type definition for anything.
            self.__typeDefinition = wxs.lookupSimpleType(node.getAttribute('type'))
        else:
            self.__typeDefinition = SimpleTypeDefinition.SimpleUrTypeDefinition()
                
        if self.SCOPE_global == self.__scope:
            if node.hasAttribute('default'):
                self.__valueConstraint = (node.getAttribute('default'), self.VC_default)
            elif node.hasAttribute('fixed'):
                self.__valueConstraint = (node.getAttribute('fixed'), self.VC_fixed)
            else:
                self.__valueConstraint = None

        # @todo handle annotation
        self.__domNode = None
        return self


class AttributeUse (_Resolvable_mixin):
    VC_na = AttributeDeclaration.VC_na
    VC_default = AttributeDeclaration.VC_default
    VC_fixer = AttributeDeclaration.VC_fixed

    # How this attribute can be used.  The component property
    # "required" is true iff the value is USE_required.
    USE_required = 0x01
    USE_optional = 0x02
    USE_prohibited = 0x04
    __use = False


    # A reference to an AttributeDeclaration
    __attributeDeclaration = None
    def attributeDeclaration (self): return self.__attributeDeclaration

    # None, or a tuple containing a string followed by one of the VC_*
    # values above.
    __valueConstraint = None
    def valueConstraint (self): return self.__valueConstraint

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        assert node.nodeName in wxs.xsQualifiedNames('attribute')
        rv = AttributeUse()
        if node.hasAttribute('use'):
            use = node.getAttribute('use')
            if 'required' == use:
                rv.__use = cls.USE_required
            elif 'optional' == use:
                rv.__use = cls.USE_optional
            elif 'prohibited' == use:
                rv.__use = cls.USE_prohibited
            else:
                raise SchemaValidationError('Unexpected value %s for attribute use attribute' % (use,))
        if not node.hasAttribute('ref'):
            # Create an anonymous declaration
            rv.__attributeDeclaration = AttributeDeclaration.CreateFromDOM(wxs, node)
        else:
            rv.__domNode = node
            wxs._queueForResolution(rv)
        return rv

    def isResolved (self):
        return self.__attributeDeclaration is not None

    def _resolve (self, wxs):
        if self.isResolved():
            return self
        assert self.__domNode
        node = self.__domNode
        if not node.hasAttribute('ref'):
            raise SchemaValidationError('Attribute uses require reference to attribute declaration')
        # Although the attribute declaration definition may not be
        # resolved, *this* component is resolved, since we don't look
        # into the attribute declaration for anything.
        self.__attributeDeclaration = wxs.lookupAttribute(node.getAttribute('ref'))
        self.__domNode = None
        return self

    def required (self):
        return self.USE_required == self.__use

    def prohibited (self):
        return self.USE_prohibited == self.__use
    
class ElementDeclaration (_NamedComponent_mixin, _Resolvable_mixin):

    # Simple or complex type definition
    __typeDefinition = None
    def typeDefinition (self): return self.__typeDefinition

    SCOPE_global = 0x01         #<<< Marker for global scope

    # The value SCOPE_global, or a complex type definition.  @todo
    # Absent for declarations in named model groups (viz., local
    # elements that aren't references).
    __scope = None
    def scope (self): return self.__scope

    VC_na = AttributeDeclaration.VC_na
    VC_default = AttributeDeclaration.VC_default
    VC_fixer = AttributeDeclaration.VC_fixed

    # None, or a tuple containing a string followed by one of the VC_*
    # values above.
    __valueConstraint = None
    def valueConstraint (self): return self.__valueConstraint

    __nillable = False
    def nillable (self): return self.__nillable

    __identityConstraintDefinitions = None

    # None, or a reference to an ElementDeclaration
    __substitutionGroupAffiliation = None

    SGE_none = 0
    SGE_extension = 0x01
    SGE_restriction = 0x02
    SGE_substitution = 0x04

    # Subset of SGE marks formed by bitmask.  SGE_substitution is disallowed.
    __substitutionGroupExclusions = SGE_none

    # Subset of SGE marks formed by bitmask
    __disallowedSubstitutions = SGE_none

    __abstract = False

    __annotation = None
    
    # The containing component which will ultimately provide the
    # scope.  None if at the top level, or a ComplexTypeDefinition or
    # a ModelGroup.
    __ancestorComponent = None

    def __init__ (self, name, target_namespace, ancestor_component):
        _NamedComponent_mixin.__init__(self, name, target_namespace)
        _Resolvable_mixin.__init__(self)
        self.__ancestorComponent = ancestor_component

    @classmethod
    def CreateFromDOM (cls, wxs, node, ancestor_component=None):
        # Node should be an XMLSchema element node
        assert node.nodeName in wxs.xsQualifiedNames('element')

        # Might be top-level, might be local
        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')

        scope = None
        namespace = None
        if node.parentNode.nodeName in wxs.xsQualifiedNames('schema'):
            namespace = wxs.getTargetNamespace()
            scope = cls.SCOPE_global
        elif not node.hasAttribute('ref'):
            namespace = wxs.targetNamespaceFromDOM(node, 'elementFormDefault')
            if not ancestor_component:
                raise IncompleteImplementationError("Require ancestor information for local element:\n%s\n" % (node.toxml(),))
            if isinstance(ancestor_component, ComplexTypeDefinition):
                scope = ancestor_component
        else:
            raise LogicError('Created reference as element declaration')
        
        rv = cls(name, namespace, ancestor_component)
        rv.__scope = scope

        # Creation does not attempt to do resolution.  Queue up the newly created
        # whatsis so we can resolve it after everything's been read in.
        rv.__domNode = node
        wxs._queueForResolution(rv)
        
        return rv

    def isResolved (self):
        return self.__typeDefinition is not None

    def _resolve (self, wxs):
        if self.isResolved():
            return self
        node = self.__domNode

        # NB: Scope already set

        if node.hasAttribute('substitutionGroup'):
            sga = wxs.lookupElement(node.getAttribute('substitutionGroup'))
            if not sga.isResolved():
                wxs._queueForResolution(self)
                return self
            self.__substitutionGroupAffiliation = sga
            
        type_def = None
        td_node = LocateUniqueChild(node, wxs, 'simpleType')
        if td_node is not None:
            type_def = SimpleTypeDefinition.CreateFromDOM(wxs, node)
        else:
            td_node = LocateUniqueChild(node, wxs, 'complexType')
            if td_node is not None:
                type_def = ComplexTypeDefinition.CreateFromDOM(wxs, td_node)
        if type_def is None:
            if node.hasAttribute('type'):
                type_def = wxs.lookupType(node.getAttribute('type'))
            elif self.__substitutionGroupAffiliation is not None:
                type_def = self.__substitutionGroupAffiliation.typeDefinition()
            else:
                type_def = ComplexTypeDefinition.UrTypeDefinition()
        self.__typeDefinition = type_def

        if node.hasAttribute('nillable'):
            self.__nillable = datatypes.boolean.StringToPython(node.getAttribute('nillable'))

        if self.SCOPE_global == self.__scope:
            if node.hasAttribute('default'):
                self.__valueConstraint = (node.getAttribute('default'), self.VC_default)
            elif node.hasAttribute('fixed'):
                self.__valueConstraint = (node.getAttribute('fixed'), self.VC_fixed)
            else:
                self.__valueConstraint = None

        # @todo identity constraints, disallowed substitutions, substitution group exclusions
                
        if node.hasAttribute('abstract'):
            self.__abstract = datatypes.boolean.StringToPython(node.getAttribute('abstract'))
                
        self.__annotation = LocateUniqueChild(node, wxs, 'annotation')

        self.__domNode = None
        return self

class ComplexTypeDefinition (_NamedComponent_mixin, _Resolvable_mixin):
    # The type resolved from the base attribute
    __baseTypeDefinition = None

    DM_empty = 0                #<<< No derivation method specified
    DM_extension = 0x01         #<<< Derivation by extension
    DM_restriction = 0x02       #<<< Derivation by restriction

    # How the type was derived.  This field is used to identify
    # unresolved definitions.
    __derivationMethod = None

    # Derived from the final and finalDefault attributes
    __final = DM_empty

    # Derived from the abstract attribute
    __abstract = False
    
    # A frozenset() of AttributeUse instances
    __attributeUses = None

    # Optional wildcard that constrains attributes
    __attributeWildcard = None

    CT_EMPTY = 0                #<<< No content
    CT_SIMPLE = 1               #<<< Simple (character) content
    CT_MIXED = 2                #<<< Children may be elements or other (e.g., character) content
    CT_ELEMENT_ONLY = 3         #<<< Expect only element content.

    # Identify the sort of content in this type.  Valid values are:
    # CT_EMPTY
    # ( CT_SIMPLE, simple_type_definition )
    # ( CT_MIXED, particle )
    # ( CT_ELEMENT_ONLY, particle )
    __contentType = None

    # Derived from the block and blockDefault attributes
    __prohibitedSubstitutions = DM_empty

    # Extracted from children of various types
    __annotations = None
    
    def __init__ (self, local_name, target_namespace, derivation_method):
        _NamedComponent_mixin.__init__(self, local_name, target_namespace)
        _Resolvable_mixin.__init__(self)
        self.__targetNamespace = target_namespace
        self.__derivationMethod = derivation_method

    def _setFromInstance (self, other):
        """Override fields in this instance with those from the other.

        This method is invoked only by Schema._addNamedComponent, and
        then only when a built-in type collides with a schema-defined
        type.  Material like facets is not (currently) held in the
        built-in copy, so the DOM information is copied over to the
        built-in STD, which is subsequently re-resolved.

        Returns self.
        """
        assert self.isNameEquivalent(other)

        # The other STD should be an unresolved schema-defined type.
        assert other.__derivationMethod is None
        assert other.__domNode is not None
        self.__domNode = other.__domNode

        # Mark this instance as unresolved so it is re-examined
        self.__derivationMethod = None
        return self

    __UrTypeDefinition = None
    @classmethod
    def UrTypeDefinition (cls, in_builtin_definition=False):
        """Create the ComplexTypeDefinition instance that approximates
        the ur-type.

        See section 3.4.7.
        """

        # The first time, and only the first time, this is called, a
        # namespace should be provided which is the XMLSchema
        # namespace for this run of the system.  Please, do not try to
        # allow this by clearing the type definition.
        if in_builtin_definition and (cls.__UrTypeDefinition is not None):
            raise LogicError('Multiple definitions of UrType')
        if cls.__UrTypeDefinition is None:
            bi = ComplexTypeDefinition('anyType', Namespace.XMLSchema, cls.DM_restriction)

            # The ur-type is its own baseTypeDefinition
            bi.__baseTypeDefinition = bi

            # No constraints on attributes
            bi.__attributeWildcard = Wildcard(Wildcard.NC_any, Wildcard.PC_lax)

            # Content is mixed, with elements completely unconstrained.
            w = Wildcard(Wildcard.NC_any, Wildcard.PC_lax)
            p = Particle(bi.__attributeWildcard, 0, None)
            m = ModelGroup(ModelGroup.C_SEQUENCE, [ p ])
            bi.__contentType = ( m, cls.CT_MIXED )

            # No attribute uses
            bi.__attributeUses = set()

            # No constraints on extension or substitution
            bi.__final = cls.DM_empty
            bi.__prohibitedSubstitutions = cls.DM_empty

            bi.__abstract = False

            # The ur-type is always resolved
            cls.__UrTypeDefinition = bi
        return cls.__UrTypeDefinition

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        # Node should be an XMLSchema complexType node
        assert node.nodeName in wxs.xsQualifiedNames('complexType')

        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')

        rv = cls(name, wxs.getTargetNamespace(), None)

        # Creation does not attempt to do resolution.  Queue up the newly created
        # whatsis so we can resolve it after everything's been read in.
        rv.__domNode = node
        wxs._queueForResolution(rv)
        
        return rv

    # Handle attributeUses, attributeWildcard, contentType
    def __completeProcessing (self, wxs, definition_node_list, method, content_style):
        uses_c1 = set()
        uses_c2 = set()
        uses_c3 = set()
        xs_attribute = wxs.xsQualifiedNames('attribute')
        xs_attributeGroup = wxs.xsQualifiedNames('attributeGroup')
        # Handle clauses 1 and 2
        for node in definition_node_list:
            if Node.ELEMENT_NODE != node.nodeType:
                continue
            if node.nodeName in xs_attribute:
                # Note: This attribute use instance may have use=prohibited
                uses_c1.add(AttributeUse.CreateFromDOM(wxs, node))
            elif node.nodeName in xs_attributeGroup:
                # This must be an attributeGroupRef
                if not node.hasAttribute('ref'):
                    raise SchemaValidationError('Require ref attribute on internal attributeGroup elements')
                agd = wxs.lookupAttributeGroup(node.getAttribute('ref'))
                if not agd.isResolved():
                    print 'Holding off resolution of attribute gruop %s due to dependence on unresolved %s' % (self.name(), agd.name())
                    wxs._queueForResolution(self)
                    return self
                uses_c2.update(agd.attributeUses())

        # Handle clause 3.  Note the slight difference in description
        # between smple and complex content is just that the complex
        # content assumes the base type definition is a complex type
        # definition.  So the same code should work for both, and we
        # don't bother to check content_style.
        if isinstance(self.__baseTypeDefinition, ComplexTypeDefinition):
            uses_c3 = uses_c3.union(self.__baseTypeDefinition.__attributeUses)
            if self.DM_restriction == self.__derivationMethod:
                # Exclude attributes per clause 3.  Note that this
                # process handles both 3.1 and 3.2, since we have
                # not yet filtered uses_c1 for prohibited attributes
                uses_c12 = uses_c1.union(uses_c2)
                for au in uses_c12:
                    uses_c3 = uses_c3.difference(au.matchingQNameMembers(uses_c3))
        uses = set([ _au for _au in uses_c1 if not _au.prohibited() ])
        self.__attributeUses = frozenset(uses.union(uses_c2).union(uses_c3))
        # @todo Handle attributeWildcard
        # Only now that we've succeeded do we set the method (mark this resolved)
        self.__derivationMethod = method
        return self

    def __completeSimpleResolution (self, wxs, definition_node_list, method, base_type):
        # deriviationMethod is assigned after resolution completes
        self.__baseTypeDefinition = base_type

        # Do content type
        if isinstance(self.__baseTypeDefinition, ComplexTypeDefinition):
            # Clauses 1, 2, and 3 might apply
            parent_content_type = self.__baseTypeDefinition.__contentType
            if (isinstance(parent_content_type, SimpleTypeDefinition) \
                    and (self.DM_restriction == method)):
                # Clause 1
                raise IncompleteImplementationError("contentType clause 1 of simple content in CTD")
            elif ((type(parent_content_type) == tuple) \
                    and (self.CT_mixed == parent_content_type[1]) \
                    and parent_content_type[0].isEmptiable()):
                # Clause 2
                raise IncompleteImplementationError("contentType clause 2 of simple content in CTD")
            else:
                # Clause 3
                raise IncompleteImplementationError("contentType clause 3 of simple content in CTD")
        else:
            # Clause 4
            self.__contentType = self.__baseTypeDefinition
                
        return self.__completeProcessing(wxs, definition_node_list, method, 'simple')

    def __completeComplexResolution (self, wxs, type_node, content_node, definition_node_list, method, base_type):
        # deriviationMethod is assigned after resolution completes
        self.__baseTypeDefinition = base_type

        # Do content type

        # Definition 1: effective mixed
        if (content_node is not None) \
                and content_node.hasAttribute('mixed'):
            effective_mixed = datatypes.boolean.StringToPython(content_node.getAttribute('mixed'))
        elif type_node.hasAttribute('mixed'):
            effective_mixed = datatypes.boolean.StringToPython(type_node.getAttribute('mixed'))
        else:
            effective_mixed = False

        # Definition 2: effective content
        case_2_1_predicate_count = 0
        test_2_1_1 = True
        test_2_1_2 = False
        test_2_1_3 = False
        typedef_particle_tags = Particle.TypedefTags(wxs)
        typedef_node = None
        allseq_particle_tags = []
        [ allseq_particle_tags.extend(wxs.xsQualifiedNames(_tag)) for _tag in [ 'all', 'sequence' ] ]
        xs_choice = wxs.xsQualifiedNames('choice')
        for cn in definition_node_list:
            if Node.ELEMENT_NODE != cn.nodeType:
                continue
            if cn.nodeName in typedef_particle_tags:
                typedef_node = cn
                test_2_1_1 = False
            if ((cn.nodeName in allseq_particle_tags) \
                    and (not HasNonAnnotationChild(wxs, cn))):
                test_2_1_2 = True
            if ((cn.nodeName in xs_choice) \
                    and (not HasNonAnnotationChild(wxs, cn))\
                    and cn.hasAttribute('minOccurs') \
                    and (0 == datatypes.integer.StringToValue(cn.getAttribute('minOccurs')))):
                test_2_1_3 = True
        satisfied_predicates = 0
        if test_2_1_1:
            satisfied_predicates += 1
        if test_2_1_2:
            satisfied_predicates += 1
        if test_2_1_3:
            satisfied_predicates += 1
        if 1 == satisfied_predicates:
            if effective_mixed:
                # Clause 2.1.4
                assert typedef_node is None
                m = ModelGroup(ModelGroup.C_SEQUENCE, [])
                effective_content = Particle(m, 1, 1)
            else:
                # Clause 2.1.5
                effective_content = self.CT_EMPTY
        else:
            # Clause 2.2
            assert typedef_node is not None
            effective_content = Particle.CreateFromDOM(wxs, typedef_node, self)

        # Shared from clause 3.1.2
        if effective_mixed:
            ct = self.CT_MIXED
        else:
            ct = self.CT_ELEMENT_ONLY
        # Clause 3
        if self.DM_restriction == method:
            # Clause 3.1
            if self.CT_EMPTY == effective_content:
                # Clause 3.1.1
                content_type = self.CT_EMPTY
            else:
                # Clause 3.1.2(.2)
                content_type = ( ct, effective_content )
        else:
            # Clause 3.2
            assert self.DM_extension == method
            assert self.__baseTypeDefinition.isResolved()
            parent_content_type = self.__baseTypeDefinition.contentType()
            if self.CT_EMPTY == effective_content:
                content_type = parent_content_type
            elif self.CT_EMPTY == parent_content_type:
                # Clause 3.2.2
                content_type = ( ct, effective_content )
            else:
                assert type(parent_content_type) == tuple
                m = ModelGroup(ModelGroup.C_SEQUENCE, [ parent_content_type[1], effective_content ])
                content_type = ( ct, Particle(m, 1, 1) )

        assert (self.CT_EMPTY == content_type) or (type(content_type) == tuple)
        self.__contentType = content_type
        return self.__completeProcessing(wxs, definition_node_list, method, 'complex')

    def isResolved (self):
        """Indicate whether this complex type is fully defined.
        
        All built-in type definitions are resolved upon creation.
        Schema-defined type definitionss are held unresolved until the
        schema has been completely read, so that references to later
        schema-defined types can be resolved.  Resolution is performed
        after the entire schema has been scanned and type-definition
        instances created for all topLevel{Simple,Complex}Types.

        If a built-in type definition is also defined in a schema
        (which it should be), the built-in definition is kept, with
        the schema-related information copied over from the matching
        schema-defined type definition.  The former then replaces the
        latter in the list of type definitions to be resolved.  See
        Schema._addNamedComponent.
        """
        # Only unresolved nodes have an unset derivationMethod
        return (self.__derivationMethod is not None)

    def _resolve (self, wxs):
        if self.isResolved():
            return self
        assert self.__domNode
        node = self.__domNode
        
        #print 'Resolving CTD %s' % (self.name(),)
        if node.hasAttribute('abstract'):
            self.__abstract = datatypes.boolean.StringToPython(node.getAttribute('abstract'))

        # @todo implement prohibitedSubstitutions, final, annotations

        # Assume we're in the short-hand case: the entire content is
        # implicitly wrapped in a complex restriction of the ur-type.
        definition_node_list = node.childNodes
        is_complex_content = True
        base_type = ComplexTypeDefinition.UrTypeDefinition()
        method = self.DM_restriction

        # Determine whether above assumption is correct by looking for
        # element content and seeing if it's one of the wrapper
        # elements.
        first_elt = LocateFirstChildElement(node)
        content_node = None
        if first_elt:
            have_content = False
            if first_elt.nodeName in wxs.xsQualifiedNames('simpleContent'):
                have_content = True
                is_complex_content = False
            elif first_elt.nodeName in wxs.xsQualifiedNames('complexContent'):
                have_content = True
            if have_content:
                # Repeat the search to verify that only the one child is present.
                content_node = LocateFirstChildElement(node, require_unique=True)
                assert content_node == first_elt
                
                # Identify the contained restriction or extension
                # element, and extract the base type.
                ions = LocateFirstChildElement(content_node, absent_ok=False)
                if ions.nodeName in wxs.xsQualifiedNames('restriction'):
                    method = self.DM_restriction
                elif ions.nodeName in wxs.xsQualifiedNames('extension'):
                    method = self.DM_extension
                else:
                    raise SchemaValidationError('Expected restriction or extension as sole child of %s in %s' % (content_node.name(), self.name()))
                if not ions.hasAttribute('base'):
                    raise SchemaValidationError('Element %s missing base attribute' % (ions.nodeName,))
                base_type = wxs.lookupType(ions.getAttribute('base'))
                if not base_type.isResolved():
                    # Have to delay resolution until the type this
                    # depends on is available.
                    print 'Holding off resolution of %s due to dependence on unresolved %s' % (self.name(), base_type.name())
                    wxs._queueForResolution(self)
                    return self
                # The content is defined by the restriction/extension element
                definition_node_list = ions.childNodes
        if is_complex_content:
            self.__completeComplexResolution(wxs, node, content_node, definition_node_list, method, base_type)
        else:
            self.__completeSimpleResolution(wxs, definition_node_list, method, base_type)
        return self

    def contentType (self):
        return self.__contentType

class AttributeGroupDefinition (_NamedComponent_mixin, _Resolvable_mixin):
    __attributeUses = None

    # Optional wildcard that constrains attributes
    __attributeWildcard = None

    # Optional annotation
    __annotation = None

    def __init__ (self, local_name, target_namespace):
        _NamedComponent_mixin.__init__(self, local_name, target_namespace)
        _Resolvable_mixin.__init__(self)

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        assert node.nodeName in wxs.xsQualifiedNames('attributeGroup')
        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')

        rv = cls(name, wxs.getTargetNamespace())

        wxs._queueForResolution(rv)
        rv.__domNode = node
        return rv

    # Indicates whether we have resolved any references
    __isResolved = False
    def isResolved (self):
        return self.__isResolved

    def _resolve (self, wxs):
        if self.__isResolved:
            return self
        node = self.__domNode
        #print 'Resolving AG %s with %d children' % (self.name(), len(node.childNodes))
        uses = set()
        if node.hasAttribute('ref'):
            agd = wxs.lookupAttributeGroup(node.getAttribute('ref'))
            if not agd.isResolved():
                print 'Holding off resolution of attribute group %s due to dependence on unresolved %s' % (self.name(), agd.name())
                wxs._queueForResolution(self)
                return self
            uses = uses.union(agd.attributeUses())
        # @todo Handle annotations
        xs_attribute = wxs.xsQualifiedNames('attribute')
        for cn in node.childNodes:
            if Node.ELEMENT_NODE != cn.nodeType:
                continue
            if cn.nodeName not in xs_attribute:
                continue
            print 'Adding use from %s' % (cn.toxml(),)
            uses.add(AttributeUse.CreateFromDOM(wxs, cn))

        self.__attributeUses = frozenset(uses)
        self.__isResolved = True
        self.__domNode = None
        
    def attributeUses (self):
        return self.__attributeUses

class ModelGroupDefinition (_NamedComponent_mixin):
    # Reference to a _ModelGroup
    __modelGroup = None

    # Optional
    __annotation = None

    def __init__ (self, name, target_namespace):
        _NamedComponent_mixin.__init__(self, name, target_namespace)

    def modelGroup (self):
        return self.__modelGroup

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        assert node.nodeName in wxs.xsQualifiedNames('group')

        assert not node.hasAttribute('ref')

        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')
        rv = cls(name, wxs.getTargetNamespace())

        mg_tags = ModelGroup.GroupMemberTags(wxs)
        for cn in node.childNodes:
            if Node.ELEMENT_NODE != cn.nodeType:
                continue
            if cn.nodeName in mg_tags:
                assert not rv.__modelGroup
                rv.__modelGroup = ModelGroup.CreateFromDOM(wxs, cn)
        rv.__annotation = LocateUniqueChild(node, wxs, 'annotation')
        return rv

class ModelGroup:
    C_INVALID = 0
    C_ALL = 0x01
    C_CHOICE = 0x02
    C_SEQUENCE = 0x03

    # One of the C_* values above
    __compositor = C_INVALID

    # A list of _Particle instances
    __particles = None

    # Optional
    __annotation = None

    def __init__ (self, compositor, particles=[]):
        self.__compositor = compositor
        self.__particles =[ _p._setAncestorComponent(self) for _p in  particles ]

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        if node.nodeName in wxs.xsQualifiedNames('all'):
            compositor = cls.C_ALL
        elif node.nodeName in wxs.xsQualifiedNames('choice'):
            compositor = cls.C_CHOICE
        elif node.nodeName in wxs.xsQualifiedNames('sequence'):
            compositor = cls.C_SEQUENCE
        else:
            raise IncompleteImplementationError('ModelGroup: Got unexpected %s' % (node.nodeName,))
        particles = []
        particle_tags = Particle.ParticleTags(wxs)
        for cn in node.childNodes:
            if Node.ELEMENT_NODE != cn.nodeType:
                continue
            if cn.nodeName in particle_tags:
                # NB: Ancestor of particle is set in the ModelGroup constructor
                particles.append(Particle.CreateFromDOM(wxs, cn, None))
        return cls(compositor, particles)

    @classmethod
    def GroupMemberTags (cls, wxs):
        return [ wxs.xsQualifiedName(_tag) for _tag in [ 'all', 'choice', 'sequence' ] ]

class Particle (_Resolvable_mixin):
    # NB: Particles are not resolvable, but the term they include
    # probably has some resolvable component.

    # The minimum number of times the term may appear; defaults to 1
    __minOccurs = 1

    # If None, the term may appear any number of times; otherwise,
    # this is an integral value indicating the maximum number of times
    # the term may appear.  The default value is 1; the value, unless
    # None, must always be at least __minOccurs.
    __maxOccurs = 1

    # A reference to a particle, which is a ModelGroup, Wildcard, or
    # ElementDeclaration
    __term = None

    # If this particle is within a complexType or a group, we need the
    # corresponding ComplexTypeDefinition or ModelGroup in order to
    # handle non-reference local elements.
    __ancestorComponent = None

    def __init__ (self, term, min_occurs=1, max_occurs=1, ancestor_component=None):
        _Resolvable_mixin.__init__(self)
        self.__term = term
        # @todo Figure out how to test whether the parameters are integers,
        # given that sometimes they're ints and sometimes they're longs
        self.__minOccurs = min_occurs
        self.__maxOccurs = max_occurs
        if self.__maxOccurs is not None:
            if self.__minOccurs > self.__maxOccurs:
                raise LogicError('Particle minOccurs %s is greater than maxOccurs %s on creation' % (min_occurs, max_occurs))
        self.__ancestorComponent = ancestor_component
        assert (self.__ancestorComponent is None) or isinstance(self.__ancestorComponent, ( ComplexTypeDefinition, ModelGroup ))
    
    def _setAncestorComponent (self, ancestor_component):
        self.__ancestorComponent = ancestor_component

    @classmethod
    def CreateFromDOM (cls, wxs, node, ancestor_component):
        min_occurs = 1
        max_occurs = 1
        if not node.nodeName in cls.ParticleTags(wxs):
            raise LogicError('Attempted to create particle from illegal element %s' % (node.nodeName,))
        if node.hasAttribute('minOccurs'):
            min_occurs = datatypes.nonNegativeInteger.StringToPython(node.getAttribute('minOccurs'))
        if node.hasAttribute('maxOccurs'):
            av = node.getAttribute('maxOccurs')
            if 'unbounded' == av:
                max_occurs = None
            else:
                max_occurs = datatypes.nonNegativeInteger.StringToPython(av)

        rv = cls(None, min_occurs, max_occurs, ancestor_component)
        rv.__domNode = node
        wxs._queueForResolution(rv)

        return rv

    def isResolved (self):
        return self.__term is not None

    def _resolve (self, wxs):
        if self.isResolved():
            return self
        #print 'Resolving Particle'
        node = self.__domNode

        if node.nodeName in wxs.xsQualifiedNames('group'):
            # 3.9.2 says use 3.8.2, which is ModelGroup.  The group
            # inside a particle is a groupRef.  If there is no group
            # with that name, this throws an exception as expected.
            if not node.hasAttribute('ref'):
                raise SchemaValidationError('group particle without reference')
            group_decl = wxs.lookupGroup(node.getAttribute('ref'))

            # Neither group definitions, nor model groups, require
            # resolution, so we can just extract the reference.
            term = group_decl.modelGroup()
        elif node.nodeName in wxs.xsQualifiedNames('element'):
            assert wxs.xsQualifiedName('schema') != node.parentNode.nodeName
            # 3.9.2 says use 3.3.2, which is Element.  The element
            # inside a particle is a localElement, so we either get
            # the one it refers to, or create an anonymous one here.
            if node.hasAttribute('ref'):
                term = wxs.lookupElement(node.getAttribute('ref'))
            else:
                term = ElementDeclaration.CreateFromDOM(wxs, node, self.__ancestorComponent)
        elif node.nodeName in wxs.xsQualifiedNames('any'):
            # 3.9.2 says use 3.10.2, which is Wildcard.
            term = Wildcard.CreateFromDOM(wxs, node)
        elif node.nodeName in ModelGroup.GroupMemberTags(wxs):
            # Choice, sequence, and all inside a particle are explicit
            # groups (or a restriction of explicit group, in the case
            # of all)
            term = ModelGroup.CreateFromDOM(wxs, node)
        else:
            raise LogicError('Unhandled node in Particle._resolve: %s' % (node.toxml(),))
        self.__term = term
        self.__domNode = None
        return self
        
    @classmethod
    def TypedefTags (cls, wxs):
        return [ wxs.xsQualifiedName(_tag) for _tag in [ 'group', 'all', 'choice', 'sequence' ] ]

    @classmethod
    def ParticleTags (cls, wxs):
        return [ wxs.xsQualifiedName(_tag) for _tag in [ 'group', 'all', 'choice', 'sequence', 'element', 'any' ] ]


# 3.10.1
class Wildcard:
    NC_any = '##any'            #<<< The namespace constraint "##any"
    NC_not = '##other'          #<<< A flag indicating constraint "##other"
    NC_targetNamespace = '##targetNamespace'
    NC_local = '##local'

    # A constraint on the namespace.  Valid values are:
    # NC_any
    # ( NC_not, a_namespace)
    # set(of_namespaces)
    # Absent is represented by None, both in the "not" pair and in the set.

    # Note that namespace are represented by Namespace instances, not
    # the URIs that actually define a namespace.
    __namespaceConstraint = None

    PC_skip = 'skip'            #<<< No constraint is applied
    PC_lax = 'lax'              #<<< Validate against available uniquely determined declaration
    PC_strict = 'strict'        #<<< Validate against declaration or xsi:type which must be available

    # One of PC_*
    __processContents = None

    __annotation = None

    def __init__ (self, namespace_constraint, process_contents):
        self.__namespaceConstraint = namespace_constraint
        self.__processContents = process_contents

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        
        if not node.hasAttribute('namespace'):
            namespace_constraint = cls.NC_any
        else:
            nc = node.getAttribute('namespace')
            if cls.NC_any == nc:
                namespace_constraint = cls.NC_any
            elif cls.NC_not == nc:
                namespace_constraint = ( cls.NC_not, wxs.getTargetNamespace() )
            else:
                ncs = set()
                for ns_uri in nc.split():
                    if cls.NC_local == ns_uri:
                        ncs.add(None)
                    elif cls.NC_targetNamespace == ns_uri:
                        ncs.add(wxs.getTargetNamespace())
                    else:
                        namespace = Namespace.NamespaceForURI(ns_uri)
                        if namespace is None:
                            namespace = Namespace.Namespace(ns_uri)
                        ncs.add(namespace)
                namespace_constraint = frozenset(ncs)

        if not node.hasAttribute('processContents'):
            process_contents = cls.PC_strict
        else:
            pc = node.getAttribute('processContents')
            if pc in [ cls.PC_skip, cls.PC_lax, cls.PC_strict ]:
                process_contents = pc
            else:
                raise SchemaValidationError('illegal value "%s" for any processContents attribute' % (pc,))

        rv = cls(namespace_constraint, process_contents)
        rv.__annotation = LocateUniqueChild(node, wxs, 'annotation')

# 3.11.1
class IdentityConstraintDefinition (_NamedComponent_mixin):
    ICC_KEY = 0x01
    ICC_KEYREF = 0x02
    ICC_UNIQUE = 0x04
    __identityConstraintCategory = None
    __selector = None
    __fields = None
    __referencedKey = None
    __annotation = None

# 3.12.1
class NotationDeclaration (_NamedComponent_mixin):
    __systemIdentifier = None
    __publicIdentifier = None
    __annotation = None

# 3.13.1
class Annotation:
    __applicationInformation = None
    __userInformation = None
    __attributes = None

    def __init__ (self):
        self.__applicationInformation = []
        self.__userInformation = []

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        rv = Annotation()
        # Node should be an XMLSchema annotation node
        assert node.nodeName in wxs.xsQualifiedNames('annotation')
        for cn in node.childNodes:
            if cn.nodeName in wxs.xsQualifiedNames('appinfo'):
                rv.__applicationInformation.append(cn)
            elif cn.nodeName in wxs.xsQualifiedNames('documentation'):
                rv.__userInformation.append(cn)
            else:
                pass
        return rv

    def __str__ (self):
        text = []
        # Values in userInformation are DOM "documentation" elements.
        # We want their combined content.
        for dn in self.__userInformation:
            for cn in dn.childNodes:
                if Node.TEXT_NODE == cn.nodeType:
                    text.append(cn.data)
        return ''.join(text)


# Section 3.14.
class SimpleTypeDefinition (_NamedComponent_mixin, _Resolvable_mixin):
    """The schema component for simple type definitions.

    This component supports the basic datatypes of XML schema, and
    those that define the values for attributes.

    @see PythonSimpleTypeSupport for additional information.
    """

    # Reference to the SimpleTypeDefinition on which this is based.
    # The value must be non-None except for the simple ur-type
    # definition.
    __baseTypeDefinition = None

    # @todo Support facets
    __facets = None
    # @todo Support fundamentalFacets
    __fundamentalFacets = None

    STD_empty = 0     #<<< Marker indicating an empty set of STD forms
    STD_extension = 0x01 #<<< Representation for extension in a set of STD forms
    STD_list = 0x02    #<<< Representation for list in a set of STD forms
    STD_restriction = 0x04 #<<< Representation of restriction in a set of STD forms
    STD_union = 0x08   #<<< Representation of union in a set of STD forms

    # Bitmask defining the subset that comprises the final property
    __final = STD_empty

    VARIETY_absent = 0x01       #<<< Only used for the ur-type
    VARIETY_atomic = 0x02       #<<< Use for types based on a primitive type
    VARIETY_list = 0x03         #<<< Use for lists of atomic-variety types
    VARIETY_union = 0x04        #<<< Use for types that aggregate other types

    # Identify the sort of value collection this holds.  This field is
    # used to identify unresolved definitions.
    __variety = None

    # For atomic variety only, the root (excepting ur-type) type.
    __primitiveTypeDefinition = None

    # For list variety only, the type of items in the list
    __itemTypeDefinition = None

    # For union variety only, the sequence of candidate members
    __memberTypeDefinitions = None

    # An annotation associated with the type
    __annotation = None

    # A non-property field that holds a reference to the DOM node from
    # which the type is defined.  The value is held only between the
    # point where the simple type definition instance is created until
    # the point it is resolved.
    __domNode = None
    
    # Indicate that this instance was defined as a built-in rather
    # than from a DOM instance.
    __isBuiltin = False

    # Allocate one of these.  Users should use one of the Create*
    # factory methods instead.  In an attempt to keep users from
    # creating these directly rather than through the approved factory
    # methods, the signature does not provide defaults for the core
    # attributes.
    def __init__ (self, name, target_namespace, variety):
        _NamedComponent_mixin.__init__(self, name, target_namespace)
        _Resolvable_mixin.__init__(self)
        self.__variety = variety

    def _setFromInstance (self, other):
        """Override fields in this instance with those from the other.

        This method is invoked only by Schema._addNamedComponent, and
        then only when a built-in type collides with a schema-defined
        type.  Material like facets is not (currently) held in the
        built-in copy, so the DOM information is copied over to the
        built-in STD, which is subsequently re-resolved.

        Returns self.
        """
        assert self.isNameEquivalent(other)

        # The other STD should be an unresolved schema-defined type.
        assert other.__baseTypeDefinition is None
        assert other.__domNode is not None
        self.__domNode = other.__domNode

        # Mark this instance as unresolved so it is re-examined
        self.__variety = None
        return self

    def isBuiltin (self):
        """Indicate whether this simple type is a built-in type."""
        return self.__isBuiltin

    __SimpleUrTypeDefinition = None
    @classmethod
    def SimpleUrTypeDefinition (cls, in_builtin_definition=False):
        """Create the SimpleTypeDefinition instance that approximates the simple ur-type.

        See section 3.14.7.  Note that this does have to be bound to a
        provided namespace since at this point we do not have a
        namespace for XMLSchema."""

        # The first time, and only the first time, this is called, a
        # namespace should be provided which is the XMLSchema
        # namespace for this run of the system.  Please, do not try to
        # allow this by clearing the type definition.
        if in_builtin_definition and (cls.__SimpleUrTypeDefinition is not None):
            raise LogicError('Multiple definitions of SimpleUrType')
        if cls.__SimpleUrTypeDefinition is None:
            bi = cls('anySimpleType', Namespace.XMLSchema, cls.VARIETY_absent)
            bi._setPythonSupport(PythonSimpleTypeSupport())

            # The baseTypeDefinition is the ur-type.
            bi.__baseTypeDefinition = ComplexTypeDefinition.UrTypeDefinition()
            # The simple ur-type has an absent variety, not an atomic
            # variety, so does not have a primitiveTypeDefinition

            cls.__SimpleUrTypeDefinition = bi
        return cls.__SimpleUrTypeDefinition

    @classmethod
    def CreatePrimitiveInstance (cls, name, target_namespace, python_support):
        """Create a primitive simple type in the target namespace.

        This is mainly used to pre-load standard built-in primitive
        types, such as those defined by XMLSchema Datatypes.  You can
        use it for your own schemas as well, if you have special types
        that require explicit support to for Pythonic conversion.

        All parameters are required and must be non-None.
        """
        
        bi = cls(name, target_namespace, cls.VARIETY_atomic)
        bi._setPythonSupport(python_support)

        # Primitive types are based on the ur-type, and have
        # themselves as their primitive type definition.
        bi.__baseTypeDefinition = cls.SimpleUrTypeDefinition()
        bi.__primitiveTypeDefinition = bi

        # Primitive types are built-in
        bi.__isBuiltin = True
        return bi

    @classmethod
    def CreateDerivedInstance (cls, name, target_namespace, parent_std, python_support):
        """Create a derived simple type in the target namespace.

        This is used to pre-load standard built-in derived types.  You
        can use it for your own schemas as well, if you have special
        types that require explicit support to for Pythonic
        conversion.
        """
        assert parent_std
        assert parent_std.__variety in (cls.VARIETY_absent, cls.VARIETY_atomic)
        bi = cls(name, target_namespace, parent_std.__variety)
        bi._setPythonSupport(python_support)

        # We were told the base type.  If this is atomic, we re-use
        # its primitive type.  Note that these all may be in different
        # namespaces.
        bi.__baseTypeDefinition = parent_std
        if cls.VARIETY_atomic == bi.__variety:
            bi.__primitiveTypeDefinition = bi.__baseTypeDefinition.__primitiveTypeDefinition

        # Derived types are built-in
        bi.__isBuiltin = True
        return bi

    @classmethod
    def CreateListInstance (cls, name, target_namespace, item_std):
        """Create a list simple type in the target namespace.

        This is used to preload standard built-in list types.  You can
        use it for your own schemas as well, if you have special types
        that require explicit support to for Pythonic conversion; but
        note that such support is identified by the item_std.
        """
        bi = cls(name, target_namespace, cls.VARIETY_list)
        # Note: The pythonSupport__ field remains None, since list
        # instances share a class-level implementation that is based
        # on their itemTypeDefinition.

        # The base type is the ur-type.  We were given the item type.
        bi.__baseTypeDefinition = cls.SimpleUrTypeDefinition()
        assert item_std
        bi.__itemTypeDefinition = item_std

        # List types are built-in
        bi.__isBuiltin = True
        return bi

    @classmethod
    def CreateUnionInstance (cls, name, target_namespace, member_stds):
        """(Placeholder) Create a union simple type in the target namespace.

        This function has not been implemented."""
        raise IncompleteImplementationError('No support for built-in union types')

    def __singleSimpleTypeChild (self, wxs, body):
        simple_type_child = None
        for cn in body.childNodes:
            if (Node.ELEMENT_NODE == cn.nodeType):
                assert cn.nodeName in wxs.xsQualifiedNames('simpleType')
                assert not simple_type_child
                simple_type_child = cn
        assert simple_type_child
        return simple_type_child

    # The __initializeFrom* methods are responsible for setting the
    # variety and the baseTypeDefinition.  The remainder of the
    # resolution is performed by the __completeResolution method.
    # All this stuff is from section 3.14.2.

    def __initializeFromList (self, wxs, body):
        self.__variety = self.VARIETY_list
        self.__baseTypeDefinition = self.SimpleUrTypeDefinition()
        return self.__completeResolution(wxs, body, 'list')

    def __initializeFromRestriction (self, wxs, body):
        if body.hasAttribute('base'):
            # Look up the base.  If there is no registered type of
            # that name, an exception gets thrown that percolates up
            # to the user.
            base_type = wxs.lookupSimpleType(body.getAttribute('base'))
            # If the base type exists but has not yet been resolve,
            # delay processing this type until the one it depends on
            # has been completed.
            if not base_type.isResolved():
                print 'Holding off resolution of anonymous simple type due to dependence on unresolved %s' % (base_type.name(),)
                wxs._queueForResolution(self)
                return
            self.__baseTypeDefinition = base_type
        else:
            self.__baseTypeDefinition = self.SimpleUrTypeDefinition()
        self.__variety = self.__baseTypeDefinition.__variety
        return self.__completeResolution(wxs, body, 'restriction')

    def __initializeFromUnion (self, wxs, body):
        self.__variety = self.VARIETY_union
        self.__baseTypeDefinition = self.SimpleUrTypeDefinition()
        return self.__completeResolution(wxs, body, 'union')

    # Complete the resolution of some variety of STD.  Note that the
    # variety is compounded by an alternative, since there is no
    # 'restriction' variety.
    def __completeResolution (self, wxs, body, alternative):
        assert self.__variety is not None
        if self.VARIETY_absent == self.__variety:
            # The ur-type is always resolved.  So are restrictions of it,
            # which is how we might get here.
            pass
        elif self.VARIETY_atomic == self.__variety:
            # Atomic types (and their restrictions) use the primitive
            # type, which is the highest type that is below the
            # ur-type (which is not atomic).
            ptd = self
            while self.VARIETY_atomic == ptd.__variety:
                assert ptd.__baseTypeDefinition
                ptd = ptd.__baseTypeDefinition
            self.__primitiveTypeDefinition = ptd
        elif self.VARIETY_list == self.__variety:
            if 'list' == alternative:
                if body.hasAttribute('itemType'):
                    self.__itemTypeDefinition = wxs.lookupSimpleType(body.getAttribute('itemType'))
                else:
                    # NOTE: The newly created anonymous item type will
                    # not be resolved; the caller needs to handle
                    # that.
                    self.__itemTypeDefinition = self.CreateFromDOM(wxs, self.__singleSimpleTypeChild(wxs, body))
            elif 'restriction' == alternative:
                self.__itemTypeDefinition = self.__baseTypeDefinition.__itemTypeDefinition
            else:
                raise LogicError('completeResolution list variety with alternative %s' % (alternative,))
        elif self.VARIETY_union == self.__variety:
            if 'union' == alternative:
                mtd = []
                # TODO If present, need to extract names from memberTypes
                if body.hasAttribute(wxs.xsQualifiedName('memberTypes')):
                    raise IncompleteImplementationError('union needs to extract names from memberTypes')
                # NOTE: Newly created anonymous types need to be resolved
                for cn in body.childNodes:
                    if (Node.ELEMENT_NODE == cn.nodeType):
                        if cn.nodeName in wxs.xsQualifiedNames('simpleType'):
                            mtd.append(self.CreateFromDOM(wxs, cn))
            elif 'restriction' == alternative:
                assert self.__baseTypeDefinition__
                # If this fails, it's probably a use-before-def issue in the schema
                assert self.__baseTypeDefinition__.isResolved()
                mtd = self.__baseTypeDefinition.__memberTypeDefinitions
                assert mtd is not None
            else:
                raise LogicError('completeResolution union variety with alternative %s' % (alternative,))
            # Save a unique copy
            self.__memberTypeDefinitions = mtd[:]
        else:
            print 'VARIETY "%s"' % (self.__variety,)
            raise LogicError('completeResolution with variety 0x%02x' % (self.__variety,))
        self.__domNode = None
        return self

    def isResolved (self):
        """Indicate whether this simple type is fully defined.
        
        Type resolution for simple types means that the corresponding
        schema component fields have been set.  Specifically, that
        means variety, baseTypeDefinition, and the appropriate
        additional fields depending on variety.  See _resolve() for
        more information.
        """
        # Only unresolved nodes have an unset variety
        return (self.__variety is not None)

    def _resolve (self, wxs):
        """Attempt to resolve the type.

        Type resolution for simple types means that the corresponding
        schema component fields have been set.  Specifically, that
        means variety, baseTypeDefinition, and the appropriate
        additional fields depending on variety.

        All built-in STDs are resolved upon creation.  Schema-defined
        STDs are held unresolved until the schema has been completely
        read, so that references to later schema-defined STDs can be
        resolved.  Resolution is performed after the entire schema has
        been scanned and STD instances created for all
        topLevelSimpleTypes.

        If a built-in STD is also defined in a schema (which it should
        be for XMLSchema), the built-in STD is kept, with the
        schema-related information copied over from the matching
        schema-defined STD.  The former then replaces the latter in
        the list of STDs to be resolved.

        Types defined by restriction have the same variety as the type
        they restrict.  If a simple type restriction depends on an
        unresolved type, this method simply queues it for resolution
        in a later pass and returns.
        """
        if self.__variety is not None:
            return self
        #print 'Resolving STD %s' % (self.name(),)
        assert self.__domNode
        node = self.__domNode
        
        bad_instance = False
        # The guts of the node should be exactly one instance of
        # exactly one of these three types.
        candidate = LocateUniqueChild(node, wxs, 'list')
        if candidate:
            self.__initializeFromList(wxs, candidate)

        candidate = LocateUniqueChild(node, wxs, 'restriction')
        if candidate:
            if self.__variety is None:
                self.__initializeFromRestriction(wxs, candidate)
            else:
                bad_instance = True

        candidate = LocateUniqueChild(node, wxs, 'union')
        if candidate:
            if self.__variety is None:
                self.__initializeFromUnion(wxs, candidate)
            else:
                bad_instance = True

        # It is NOT an error to fail to resolve the type.
        if bad_instance:
            raise SchemaValidationError('Expected exactly one of list, restriction, union as child of simpleType')

        return self

    @classmethod
    def CreateFromDOM (cls, wxs, node):
        # Node should be an XMLSchema simpleType node
        assert node.nodeName in wxs.xsQualifiedNames('simpleType')

        # @todo Process "final" attributes
        if node.hasAttribute('final'):
            raise IncompleteImplementationError('"final" attribute not currently supported')

        name = None
        if node.hasAttribute('name'):
            name = node.getAttribute('name')

        rv = cls(name, wxs.getTargetNamespace(), None)

        # Creation does not attempt to do resolution.  Queue up the newly created
        # whatsis so we can resolve it after everything's been read in.
        rv.__domNode = node
        wxs._queueForResolution(rv)
        
        return rv

    # pythonSupport is an instance of a subclass of
    # PythonSimpleTypeSupport.  When set, this simple type definition
    # must be associated with the support instance.
    __pythonSupport = None

    def _setPythonSupport (self, python_support):
        # Includes check that python_support is not None
        assert isinstance(python_support, PythonSimpleTypeSupport)
        # Can't share support instances
        self.__pythonSupport = python_support
        self.__pythonSupport._setSimpleTypeDefinition(self)
        return self.__pythonSupport

    def pythonSupport (self):
        if self.__pythonSupport is None:
            raise LogicError('%s: No support defined' % (self.name(),))
        return self.__pythonSupport

    def stringToPython (self, string):
        return self.pythonSupport().stringToPython(string)

    def pythonToString (self, value):
        return self.pythonSupport().pythonToString(value)

class Schema (object):
    NT_type = 0x01              #<<< Name represents a simple or complex type
    NT_attributeGroup = 0x02    #<<< Name represents an attribute group definition
    NT_modelGroup = 0x03        #<<< Name represents a model group definition
    NT_attribute = 0x04         #<<< Name represents an attribute declaration
    NT_element = 0x05           #<<< Name represents an element declaration

    __typeDefinitions = None
    __attributeGroupDefinitions = None
    __modelGroupDefinitions = None
    __attributeDeclarations = None
    __elementDeclarations = None
    __notationDeclarations = None
    __annotations = None

    def __mapForNamedType (self, nt):
        if self.NT_type == nt:
            return self.__typeDefinitions
        if self.NT_attributeGroup == nt:
            return self.__attributeGroupDefinitions
        if self.NT_modelGroup == nt:
            return self.__modelGroupDefinitions
        if self.NT_attribute == nt:
            return self.__attributeDeclarations
        if self.NT_element == nt:
            return self.__elementDeclarations
        raise LogicError('Invalid named type 0x02x' % (nt,))

    __unresolvedDefinitions = None

    # Default values for standard recognized schema attributes
    __attributeMap = { 'attributeFormDefault' : 'unqualified'
                     , 'elementFormDefault' : 'unqualified'
                     , 'blockDefault' : ''
                     , 'finalDefault' : ''
                     , 'id' : None
                     , 'targetNamespace' : None
                     , 'version' : None
                     # , 'xml:lang' : None
                     } 

    def _setAttributeFromDOM (self, attr):
        self.__attributeMap[attr.name] = attr.nodeValue
        return self

    def hasAttribute (self, attr_name):
        return self.__attributeMap.has_key(attr_name)

    def getAttribute (self, attr_name):
        return self.__attributeMap[attr_name]

    def __init__ (self):
        self.__annotations = [ ]

        self.__typeDefinitions = { }
        self.__attributeGroupDefinitions = { }
        self.__modelGroupDefinitions = { }
        self.__attributeDeclarations = { }
        self.__elementDeclarations = { }

        self.__unresolvedDefinitions = []

    def _queueForResolution (self, std):
        """Invoked to note that a component may have unresolved references.

        Newly created named components are unresolved, as are
        components which, in the course of resolution, are found to
        depend on another unresolved component.
        """
        assert isinstance(std, _Resolvable_mixin)
        self.__unresolvedDefinitions.append(std)
        return std

    def __replaceUnresolvedDefinition (self, existing_def, replacement_def):
        assert existing_def in self.__unresolvedDefinitions
        self.__unresolvedDefinitions.remove(existing_def)
        assert replacement_def not in self.__unresolvedDefinitions
        assert isinstance(replacement_def, _Resolvable_mixin)
        self.__unresolvedDefinitions.append(replacement_def)
        return replacement_def

    def _resolveDefinitions (self):
        """Loop until all components associated with a name are
        sufficiently defined."""
        while self.__unresolvedDefinitions:
            # Save the list of unresolved TDs, reset the list to
            # capture any new TDs defined during resolution (or TDs
            # that depend on an unresolved type), and attempt the
            # resolution for everything that isn't resolved.
            unresolved = self.__unresolvedDefinitions
            self.__unresolvedDefinitions = []
            for std in unresolved:
                std._resolve(self)
            if self.__unresolvedDefinitions == unresolved:
                # This only happens if we didn't code things right, or
                # the schema actually has a circular dependency in
                # some named component.
                failed_components = []
                for d in self.__unresolvedDefinitions:
                    if isinstance(d, _NamedComponent_mixin):
                        failed_components.append('%s named %s' % (d.__class__.__name__, d.name()))
                    else:
                        failed_components.append('Anonymous %s' % (d.__class__.__name__,))
                raise LogicError('Infinite loop in resolution:\n  %s' % ("\n  ".join(failed_components),))
        self.__unresolvedDefinitions = None
        return self

    def _addAnnotation (self, annotation):
        self.__annotations.append(annotation)
        return annotation

    def _addNamedComponent (self, nc):
        if not isinstance(nc, _NamedComponent_mixin):
            raise LogicError('Attempt to add unnamed %s instance to dictionary' % (nc.__class__,))
        if nc.ncName() is None:
            raise LogicError('Attempt to add anonymous component to dictionary: %s', (nc.__class__,))
        #print 'Adding %s as %s' % (nc.__class__.__name__, nc.name())
        if isinstance(nc, (SimpleTypeDefinition, ComplexTypeDefinition)):
            return self.__addTypeDefinition(nc)
        if isinstance(nc, AttributeGroupDefinition):
            return self.__addAttributeGroupDefinition(nc)
        if isinstance(nc, AttributeDeclaration):
            return self.__addAttributeDeclaration(nc)
        if isinstance(nc, ModelGroupDefinition):
            return self.__addModelGroupDefinition(nc)
        if isinstance(nc, ElementDeclaration):
            return self.__addElementDeclaration(nc)
        raise IncompleteImplementationError('No support to record named component of type %s' % (nc.__class__,))

    def __addTypeDefinition (self, td):
        local_name = td.ncName()
        old_td = self.__typeDefinitions.get(local_name, None)
        if old_td is not None:
            # @todo validation error if old_td is not a built-in
            if isinstance(td, ComplexTypeDefinition) != isinstance(old_td, ComplexTypeDefinition):
                raise SchemaValidationError('Name %s used for both simple and complex types' % (td.name(),))
            # Copy schema-related information from the new definition
            # into the old one, and continue to use the old one.
            td = self.__replaceUnresolvedDefinition(td, old_td._setFromInstance(td))
        else:
            self.__typeDefinitions[local_name] = td
        return td
    
    def _typeDefinitions (self):
        return self.__typeDefinitions.values()

    def _lookupTypeDefinition (self, local_name):
        return self.__typeDefinitions.get(local_name, None)

    def __addAttributeGroupDefinition (self, agd):
        assert isinstance(agd, AttributeGroupDefinition)
        local_name = agd.ncName()
        old_agd = self.__attributeGroupDefinitions.get(local_name, None)
        if old_agd is not None:
            raise SchemaValidationError('Name %s used for multiple attribute group definitions' % (local_name,))
        self.__attributeGroupDefinitions[local_name] = agd
        return agd

    def _lookupAttributeGroupDefinition (self, local_name):
        return self.__attributeGroupDefinitions.get(local_name, None)

    def _attributeGroupDefinitions (self):
        return self.__attributeGroupDefinitions.values()

    def __addModelGroupDefinition (self, ad):
        assert isinstance(ad, ModelGroupDefinition)
        local_name = ad.ncName()
        #print 'Defining group %s' % (local_name,)
        old_ad = self.__modelGroupDefinitions.get(local_name, None)
        if old_ad is not None:
            raise SchemaValidationError('Name %s used for multiple groups' % (local_name,))
        self.__modelGroupDefinitions[local_name] = ad
        return ad

    def _lookupModelGroupDefinition (self, local_name):
        return self.__modelGroupDefinitions.get(local_name, None)

    def _modelGroupDefinitions (self):
        return self.__modelGroupDefinitions.values()

    def __addAttributeDeclaration (self, ad):
        assert isinstance(ad, AttributeDeclaration)
        local_name = ad.ncName()
        old_ad = self.__attributeDeclarations.get(local_name, None)
        if old_ad is not None:
            raise SchemaValidationError('Name %s used for multiple attribute declarations' % (local_name,))
        self.__attributeDeclarations[local_name] = ad
        return ad

    def _lookupAttributeDeclaration (self, local_name):
        return self.__attributeDeclarations.get(local_name, None)

    def _attributeDeclarations (self):
        return self.__attributeDeclarations.values()

    def __addElementDeclaration (self, ed):
        assert isinstance(ed, ElementDeclaration)
        local_name = ed.ncName()
        #print 'Defining element %s' % (local_name,)
        old_ed = self.__elementDeclarations.get(local_name, None)
        if old_ed is not None:
            raise SchemaValidationError('Name %s used for multiple elements' % (local_name,))
        self.__elementDeclarations[local_name] = ed
        return ed

    def _lookupElementDeclaration (self, local_name):
        return self.__elementDeclarations.get(local_name, None)

    def _elementDeclarations (self):
        return self.__elementDeclarations.values()

    def _lookupNamedComponent (self, ncname, component_type):
        return self.__mapForNamedType(component_type).get(ncname, None)
