(function() {
  var Annotator, util, _Annotator;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  util = {
    uuid: (function() {
      var counter;
      counter = 0;
      return function() {
        return counter++;
      };
    })(),
    getGlobal: function() {
      return (function() {
        return this;
      })();
    },
    mousePosition: function(e, offsetEl) {
      var offset;
      offset = $(offsetEl).offset();
      return {
        top: e.pageY - offset.top,
        left: e.pageX - offset.left
      };
    },
    preventEventDefault: function(event) {
      return event != null ? typeof event.preventDefault === "function" ? event.preventDefault() : void 0 : void 0;
    }
  };
  _Annotator = this.Annotator;
  Annotator = (function() {
    __extends(Annotator, Delegator);
    Annotator.prototype.events = {
      ".annotator-adder button click": "onAdderClick",
      ".annotator-adder button mousedown": "onAdderMousedown",
      ".annotator-hl mouseover": "onHighlightMouseover",
      ".annotator-hl mouseout": "startViewerHideTimer"
    };
    Annotator.prototype.html = {
      hl: '<span class="annotator-hl"></span>',
      adder: '<div class="annotator-adder"><button>' + _t('Annotate') + '</button></div>',
      wrapper: '<div class="annotator-wrapper"></div>'
    };
    Annotator.prototype.options = {};
    Annotator.prototype.plugins = {};
    Annotator.prototype.editor = null;
    Annotator.prototype.viewer = null;
    Annotator.prototype.selectedRanges = null;
    Annotator.prototype.mouseIsDown = false;
    Annotator.prototype.ignoreMouseup = false;
    Annotator.prototype.viewerHideTimer = null;
    function Annotator(element, options) {
      this.onDeleteAnnotation = __bind(this.onDeleteAnnotation, this);
      this.onEditAnnotation = __bind(this.onEditAnnotation, this);
      this.onAdderClick = __bind(this.onAdderClick, this);
      this.onAdderMousedown = __bind(this.onAdderMousedown, this);
      this.onHighlightMouseover = __bind(this.onHighlightMouseover, this);
      this.checkForEndSelection = __bind(this.checkForEndSelection, this);
      this.checkForStartSelection = __bind(this.checkForStartSelection, this);
      this.clearViewerHideTimer = __bind(this.clearViewerHideTimer, this);
      this.startViewerHideTimer = __bind(this.startViewerHideTimer, this);
      this.showViewer = __bind(this.showViewer, this);
      this.onEditorSubmit = __bind(this.onEditorSubmit, this);
      this.onEditorHide = __bind(this.onEditorHide, this);
      this.showEditor = __bind(this.showEditor, this);      var name, src, _ref;
      Annotator.__super__.constructor.apply(this, arguments);
      this.plugins = {};
      if (!Annotator.supported()) {
        return this;
      }
      this._setupDocumentEvents()._setupWrapper()._setupViewer()._setupEditor();
      _ref = this.html;
      for (name in _ref) {
        src = _ref[name];
        if (name !== 'wrapper') {
          this[name] = $(src).appendTo(this.wrapper).hide();
        }
      }
    }
    Annotator.prototype._setupWrapper = function() {
      this.wrapper = $(this.html.wrapper);
      this.element.find('script').remove();
      this.element.wrapInner(this.wrapper);
      this.wrapper = this.element.find('.annotator-wrapper');
      return this;
    };
    Annotator.prototype._setupViewer = function() {
      this.viewer = new Annotator.Viewer();
      this.viewer.hide().on("edit", this.onEditAnnotation).on("delete", this.onDeleteAnnotation).addField({
        load: __bind(function(field, annotation) {
          $(field).escape(annotation.text || '');
          return this.publish('annotationViewerTextField', [field, annotation]);
        }, this)
      }).element.appendTo(this.wrapper).bind({
        "mouseover": this.clearViewerHideTimer,
        "mouseout": this.startViewerHideTimer
      });
      return this;
    };
    Annotator.prototype._setupEditor = function() {
      this.editor = new Annotator.Editor();
      this.editor.hide().on('hide', this.onEditorHide).on('save', this.onEditorSubmit).addField({
        type: 'textarea',
        label: _t('Comments') + '\u2026',
        load: function(field, annotation) {
          return $(field).find('textarea').val(annotation.text || '');
        },
        submit: function(field, annotation) {
          return annotation.text = $(field).find('textarea').val();
        }
      });
      this.editor.element.appendTo(this.wrapper);
      return this;
    };
    Annotator.prototype._setupDocumentEvents = function() {
      $(document).bind({
        "mouseup": this.checkForEndSelection,
        "mousedown": this.checkForStartSelection
      });
      return this;
    };
    Annotator.prototype.getSelectedRanges = function() {
      var browserRange, i, ranges, selection;
      selection = util.getGlobal().getSelection();
      ranges = [];
      if (!selection.isCollapsed) {
        ranges = (function() {
          var _ref, _results;
          _results = [];
          for (i = 0, _ref = selection.rangeCount; 0 <= _ref ? i < _ref : i > _ref; 0 <= _ref ? i++ : i--) {
            browserRange = new Range.BrowserRange(selection.getRangeAt(i));
            _results.push(browserRange.normalize().limit(this.wrapper[0]));
          }
          return _results;
        }).call(this);
      }
      return $.grep(ranges, function(range) {
        return range;
      });
    };
    Annotator.prototype.createAnnotation = function() {
      var annotation;
      annotation = {};
      this.publish('beforeAnnotationCreated', [annotation]);
      return annotation;
    };
    Annotator.prototype.setupAnnotation = function(annotation, fireEvents) {
      var normed, normedRanges, r, sniffed, _i, _len;
      if (fireEvents == null) {
        fireEvents = true;
      }
      annotation.ranges || (annotation.ranges = this.selectedRanges);
      normedRanges = (function() {
        var _i, _len, _ref, _results;
        _ref = annotation.ranges;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          r = _ref[_i];
          sniffed = Range.sniff(r);
          _results.push(sniffed.normalize(this.wrapper[0]));
        }
        return _results;
      }).call(this);
      normedRanges = $.grep(normedRanges, function(range) {
        return range !== null;
      });
      annotation.quote = [];
      annotation.ranges = [];
      annotation.highlights = [];
      for (_i = 0, _len = normedRanges.length; _i < _len; _i++) {
        normed = normedRanges[_i];
        annotation.quote.push($.trim(normed.text()));
        annotation.ranges.push(normed.serialize(this.wrapper[0], '.annotator-hl'));
        $.merge(annotation.highlights, this.highlightRange(normed));
      }
      annotation.quote = annotation.quote.join(' / ');
      $(annotation.highlights).data('annotation', annotation);
      if (fireEvents) {
        this.publish('annotationCreated', [annotation]);
      }
      return annotation;
    };
    Annotator.prototype.updateAnnotation = function(annotation) {
      this.publish('beforeAnnotationUpdated', [annotation]);
      this.publish('annotationUpdated', [annotation]);
      return annotation;
    };
    Annotator.prototype.deleteAnnotation = function(annotation) {
      var h, _i, _len, _ref;
      _ref = annotation.highlights;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        h = _ref[_i];
        $(h).replaceWith(h.childNodes);
      }
      this.publish('annotationDeleted', [annotation]);
      return annotation;
    };
    Annotator.prototype.loadAnnotations = function(annotations) {
      var clone, loader;
      if (annotations == null) {
        annotations = [];
      }
      loader = __bind(function(annList) {
        var n, now, _i, _len;
        if (annList == null) {
          annList = [];
        }
        now = annList.splice(0, 10);
        for (_i = 0, _len = now.length; _i < _len; _i++) {
          n = now[_i];
          this.setupAnnotation(n, false);
        }
        if (annList.length > 0) {
          return setTimeout((function() {
            return loader(annList);
          }), 100);
        } else {
          return this.publish('annotationsLoaded', [clone]);
        }
      }, this);
      clone = annotations.slice();
      if (annotations.length) {
        loader(annotations);
      }
      return this;
    };
    Annotator.prototype.dumpAnnotations = function() {
      if (this.plugins['Store']) {
        return this.plugins['Store'].dumpAnnotations();
      } else {
        return console.warn(_t("Can't dump annotations without Store plugin."));
      }
    };
    Annotator.prototype.highlightRange = function(normedRange) {
      var elemList, node, wrapper;
      return elemList = (function() {
        var _i, _len, _ref, _results;
        _ref = normedRange.textNodes();
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          node = _ref[_i];
          wrapper = this.hl.clone().show();
          _results.push($(node).wrap(wrapper).parent().get(0));
        }
        return _results;
      }).call(this);
    };
    Annotator.prototype.addPlugin = function(name, options) {
      var klass, _base;
      if (this.plugins[name]) {
        console.error(_t("You cannot have more than one instance of any plugin."));
      } else {
        klass = Annotator.Plugin[name];
        if (typeof klass === 'function') {
          this.plugins[name] = new klass(this.element[0], options);
          this.plugins[name].annotator = this;
          if (typeof (_base = this.plugins[name]).pluginInit === "function") {
            _base.pluginInit();
          }
        } else {
          console.error(_t("Could not load ") + name + _t(" plugin. Have you included the appropriate <script> tag?"));
        }
      }
      return this;
    };
    Annotator.prototype.showEditor = function(annotation, location) {
      this.editor.element.css(location);
      this.editor.load(annotation);
      return this;
    };
    Annotator.prototype.onEditorHide = function() {
      this.publish('annotationEditorHidden', [this.editor]);
      return this.ignoreMouseup = false;
    };
    Annotator.prototype.onEditorSubmit = function(annotation) {
      this.publish('annotationEditorSubmit', [this.editor, annotation]);
      if (annotation.ranges === void 0) {
        return this.setupAnnotation(annotation);
      } else {
        return this.updateAnnotation(annotation);
      }
    };
    Annotator.prototype.showViewer = function(annotations, location) {
      this.viewer.element.css(location);
      this.viewer.load(annotations);
      return this.publish('annotationViewerShown', [this.viewer, annotations]);
    };
    Annotator.prototype.startViewerHideTimer = function() {
      if (!this.viewerHideTimer) {
        return this.viewerHideTimer = setTimeout(this.viewer.hide, 250);
      }
    };
    Annotator.prototype.clearViewerHideTimer = function() {
      clearTimeout(this.viewerHideTimer);
      return this.viewerHideTimer = false;
    };
    Annotator.prototype.checkForStartSelection = function(event) {
      if (!(event && this.isAnnotator(event.target))) {
        this.startViewerHideTimer();
        return this.mouseIsDown = true;
      }
    };
    Annotator.prototype.checkForEndSelection = function(event) {
      var container, range, _i, _len, _ref;
      this.mouseIsDown = false;
      if (this.ignoreMouseup) {
        return;
      }
      this.selectedRanges = this.getSelectedRanges();
      _ref = this.selectedRanges;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        range = _ref[_i];
        container = range.commonAncestor;
        if (this.isAnnotator(container)) {
          return;
        }
      }
      if (event && this.selectedRanges.length) {
        return this.adder.css(util.mousePosition(event, this.wrapper[0])).show();
      } else {
        return this.adder.hide();
      }
    };
    Annotator.prototype.isAnnotator = function(element) {
      return !!$(element).parents().andSelf().filter('[class^=annotator-]').not(this.wrapper).length;
    };
    Annotator.prototype.onHighlightMouseover = function(event) {
      var annotations;
      this.clearViewerHideTimer();
      if (this.mouseIsDown || this.viewer.isShown()) {
        return false;
      }
      annotations = $(event.target).parents('.annotator-hl').andSelf().map(function() {
        return $(this).data("annotation");
      });
      return this.showViewer($.makeArray(annotations), util.mousePosition(event, this.wrapper[0]));
    };
    Annotator.prototype.onAdderMousedown = function(event) {
      if (event != null) {
        event.preventDefault();
      }
      return this.ignoreMouseup = true;
    };
    Annotator.prototype.onAdderClick = function(event) {
      var position;
      if (event != null) {
        event.preventDefault();
      }
      position = this.adder.position();
      this.adder.hide();
      return this.showEditor(this.createAnnotation(), position);
    };
    Annotator.prototype.onEditAnnotation = function(annotation) {
      var offset;
      offset = this.viewer.element.position();
      this.viewer.hide();
      return this.showEditor(annotation, offset);
    };
    Annotator.prototype.onDeleteAnnotation = function(annotation) {
      this.viewer.hide();
      return this.deleteAnnotation(annotation);
    };
    return Annotator;
  })();
  Annotator.Plugin = (function() {
    __extends(Plugin, Delegator);
    function Plugin(element, options) {
      Plugin.__super__.constructor.apply(this, arguments);
    }
    Plugin.prototype.pluginInit = function() {};
    return Plugin;
  })();
  Annotator.$ = $;
  Annotator._t = _t;
  Annotator.supported = function() {
    return (function() {
      return !!this.getSelection;
    })();
  };
  Annotator.noConflict = function() {
    util.getGlobal().Annotator = _Annotator;
    return this;
  };
  $.plugin('annotator', Annotator);
  this.Annotator = Annotator;
}).call(this);
