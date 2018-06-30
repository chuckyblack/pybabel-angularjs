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


Heavily inspired by 
https://bitbucket.org/shoreware/pybabel-angularjs