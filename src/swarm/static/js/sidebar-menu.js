function initsidebarMenu(menu) {
  var animationSpeed = 200;
  
  $(menu).on('click', 'li a', function(e) {
    var $this = $(this);
    var checkElement = $this.next();
    var elements = $this.nextAll();

    if (checkElement.is('.treeview-menu') && checkElement.is(':visible')) {
      checkElement.slideUp(animationSpeed, function() {
        checkElement.removeClass('menu-open');
        elements.css("display", "none");
      });
      checkElement.parent("li").removeClass("active");
    }

    //If the menu is not visible
    else if ((checkElement.is('.treeview-menu')) && (!checkElement.is(':visible'))) {
      //Get the parent menu
      var parent = $this.parents('ul').first();
      //Close all open menus within the parent
      var ul = parent.find('ul:visible').slideUp(animationSpeed);
      //Remove the menu-open class from the parent
      ul.removeClass('menu-open');
      //Get the parent li
      var parent_li = $this.parent("li");

      //Open the target menu and add the menu-open class
      checkElement.slideDown(animationSpeed, function() {
        //Add the class active to the parent li
        checkElement.addClass('menu-open');
        parent.find('li.active').removeClass('active');
        parent_li.addClass('active');
        elements.css("display", "block");
      });
    }
    //if this isn't a link, prevent the page from being redirected
    if (checkElement.is('.treeview-menu')) {
      e.preventDefault();
    }
  });
}

function initMenuEvents() {
  function initEvents() {
    $('#menu-button').on( 'click', openMenu );
    $('#close-button').on( 'click', closeMenu );
  }

  function openMenu() {
    $('.main-sidebar').addClass('show-menu');
    $('.right-container').addClass('shrink');
    $('.menu-button').addClass('hide');
  }

  function closeMenu() {
    $('.main-sidebar').removeClass('show-menu');
    $('.right-container').removeClass('shrink');
    $('.menu-button').removeClass('hide');
  }

  initEvents();
}