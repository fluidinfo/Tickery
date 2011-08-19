TODO
====

Tasks
-----

* Get us off hacked version of txJSON-RPC (has it been upgraded yet?)
* Try running against latest Pyjamas.
* Try running against Twisted 10.1.

Additional features
-------------------

* Add API tab.
* Add a 'refresh my Twitter details button'.
* Change control perms on the tags Tickery creates, to allow the username
  to do whatever it likes, including cut off Tickery. Need to change
  Tickery so it can deal with that.
* Make status window auto-update
* Canonicalize some queries to improve cache hit ratio.
* Set a timer to periodically update # of users tracked by Tickery.
* Add a button to allow a user to update their Twitter details in Fluidinfo.
  (i.e., we spider them, update their followers etc)
* Add a refreshFromFluidinfo method to the caches that can use it.
* The cache should expire things. Switch to memcached?
* Need to re-spider users and refresh/update/expire other cache info.
* Add twitter.com/SUL tags.
* Requests to twitter (and Fluidinfo?) should have timeouts.
* Add an offline mode that only works on cached data in case Fluidinfo 
  or Twitter are down/inaccessible. Set this on/off on the admin page.
* What do we do when a user changes from public to protected?
* Setting the visible limit on the simple tab text boxes doesn't work too well.
* Hitting arrow keys (to navigate) in the icon panel should adjust large avatar.
* Add a button to click to see a Google map with icons on locations.
* Add start-up options to size the queue width, friends limit, etc

Minor bugs
----------

* Why does MSIE say "error in the page" when trying to use and/or/except
  buttons on int/adv tab?
* Why does MSIE not load the # of counted users (utils.py error line 19?)
  when tickery is made with make debug?
* The large query box changes size momentarily each time you hit Go.
* Queue pos is right aligned, work done is left aligned; looks weird.
* There's still an occasional problem with follow/unfollow in which the 
  button is not re-enabled.
* When the user logs off, Tweet This widgets should go away.
* The tweet this button does not appear if we've received result of a query
  fired via command line args but the user's login details were not yet
  available when the results came in. Clicking 'go' again will redo the
  query and the tweet this button will appear.
* Resizing the simple tab under MSIE causes it to truncate the RHS, same on FF.
* When a user's name or their location is too long (without spaces) it can
  cause the icon area to oscillate wildly as it resizes that area, which
  lands the mouse on another icon, which resizes the area, which...  So
  perhaps look at the len of the field and use a different CSS class with
  a smaller font-size in that case.
* The up/down sort char in the sort menu don't display right on MSIE 8
  under XP. Should we be setting the font more explicitly?

Admin interface improvements
----------------------------

* Show number of Twitter API calls still allowed, reset time, graph.
* Add the ability to toggle noisy logging.
* Make admin interface auto-update?
* Allow us to act on the cache.
* Allow us to rebuild or refresh from Fluidinfo.
* Ability to remove users from Fluidinfo?
* Shows usage stats.
* Should be able to send a HUP to Tickery to have caches dumped.

Possible extensions
-------------------

* Add users' last tweets, etc.
* Make a live view page to show what's being queried, what the results are.
* Add a text-only version for mobile devices? Or a mode=text arg that show
  results just as a textual username with link into twitter. 
* Can we make the Twitter auth redirect take you back to the same tab
  with the same query?  It seems like we might be able to because although
  Twitter has a registered callback for Tickery, they don't seem to use
  it as I accidentally discovered in getting things to work. We can specify
  a callback URL in the request.
* The ability to select a set of users and (un)follow them all.
* Add a way to see your own friends and put their screennames into the 
  query panel with a click. (Fergus suggestion.)
* Would be nice to provide an estimate of how long adding a user will take,
  based on the number of people ahead of them on the queue, # they follow
  and how many of those we don't already have in the system, system load,
  recent timings, etc.
