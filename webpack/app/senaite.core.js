import $ from "jquery";
import I18N from "./components/i18n.js";
import {i18n, _t, _p} from "./i18n-wrapper.js"
import EditForm from "./components/editform.js"
import Site from "./components/site.js"
import Sidebar from "./components/sidebar.js"


document.addEventListener("DOMContentLoaded", () => {
  console.info("*** SENAITE CORE JS LOADED ***");

  // Initialize i18n message factories
  window.i18n = new I18N();
  window._t = _t;
  window._p = _p;

  // BBB: set global `portal_url` variable
  window.portal_url = document.body.dataset.portalUrl

  // Initialize Site
  window.site = new Site();

  // Initialize Sidebar
  window.sidebar = new Sidebar({
    "el": "sidebar",
  });

  // Ajax Edit Form Handler
  var form = new EditForm({
    form_selectors: [
      "form[name='edit_form']",
      "form.senaite-ajax-form",
    ],
    field_selectors: [
      "input[type='text']",
      "input[type='number']",
      "input[type='checkbox']",
      "input[type='radio']",
      "input[type='file']",
      "select",
      "textarea",
    ]
  })

  // Init Tooltips
  $(function () {
    $("[data-toggle='tooltip']").tooltip();
    $("select.selectpicker").selectpicker();
  });

  // Reload the whole view if the status of the view's context has changed
  // due to the transition submission of some items from the listing
  document.body.addEventListener("listing:submit", (event) => {

    // skip site reload for multi_results view
    // TODO: find a better way for this check!
    if (document.body.classList.contains("template-multi_results")) {
      return;
    }

    // get the old workflow state of the view context
    let old_workflow_state = document.body.dataset.reviewState;

    // get the new workflow state of the view context
    // https://github.com/senaite/senaite.app.listing/pull/92
    let data = event.detail.data;
    let new_workflow_state = data.view_context_state;

    // reload the entire page if workflow state of the view context changed
    if (old_workflow_state != new_workflow_state) {
      location.reload();
    }
  });

});
