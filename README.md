pybabel-angularjs
=================

A Babel extractor for AngularJS templates.

To translate the content of an HTML element use the `i18n`
attribute:

    <div i18n>hello world!</div>

To give somme context to your translators add value to the attribute:

    <div i18n="page title">hello world!</div>

## Babel configuration

### extract_attribute

To change default `i18n` attribute use `extract_attribute` options:

    [angularjs: **/*.html]
    encoding = utf-8
    extract_attribute = translate
    
Then use in template:

    <div translate="page title">hello world!</div>
    
### include_attributes

To translate attributes of HTML nodes use `include_attributes` options:

    [angularjs: **/*.html]
    encoding = utf-8
    include_attributes = title, alt
    
Then use in template:

    <div title="some title">hello world!</div>
    <img src="..." alt="some image description">
    
    
### allowed_tags

Content of every translated tag is checked for tags it contains. You have to define sub-tags that can occur.
Tags allowed by default are: strong, br, i

    [angularjs: **/*.html]
    encoding = utf-8
    allowed_tags = a, strong, br
    
    
### allowed_attributes_x

Sub-tags (described in 'allowed_tags') may by default contain NO attributes at all.
If you want to enable them to, you have to use this notation:

    [angularjs: **/*.html]
    encoding = utf-8
    allowed_tags = a, i
    allowed_attributes_a = href
    allowed_attributes_i = class
    
The allowed_attribues_x setting needs to be accompanied by appropriate 'allowed_tags' setting. 


Heavily inspired by 
https://bitbucket.org/shoreware/pybabel-angularjs
