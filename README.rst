pybabel-angularjs
=================

A Babel extractor for use with AngularJS.

To translate the content of an HTML element use the ``data-translate``
attribute::

    <div data-translate>hello world!</div>

To handle pluralization use the ``data-translate-plural`` attribute::

    <div data-translate
         data-translate-plural="hello {$count$} worlds!">hello one world!</div>

To give somme context to your translators use the
``data-translate-comment`` attribute::

    <div data-translate
         data-translate-comment="What a beautiful world">hello world!</div>

To translate attributes of HTML nodes, use the ``data-translate-attr`` attribute::

    <a href="..."
       title="A title to translate"
       data-translate data-translate-attr="title">Some content to translate too</a>

Multiple attributes can be translated by separating them with commas::

    <img alt="Translated" title="Translated too" data-translate-attr="alt,title" />

Heavily inspired by `Angular Gettext Babel`_ and `i19`_.

.. _Angular Gettext Babel: https://github.com/neillc/angular-gettext-babel
.. _i19: https://github.com/johaness/i19
