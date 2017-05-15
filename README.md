# Custom waiting pages in oTree

## Custom first and other waiting pages for mTurk - allowing users to finish the game when they wait too long




The task of this code is to guarantee that players in online experiments won't
get stuck at the initial stage of the game while waiting for other participants.
This situation can be risky for experimenter's reputation.

There are two ways to avoid the players' anxiety caused by too long waiting
times.

1. We let them finish the game after waiting at the starting waiting page for
a certain period of time.

**Before timeout is finished at the first page**
![image2](/readmeimgs/img2.png "Image2")
**After timeout is finished at the first page**
![image1](/readmeimgs/img1.png "Image1")
2. We inform them in a real time for how many players they have to wait before
proceeding to the next page. This we will do not only at the first page, but
in all waiting pages in the game.
![image3](/readmeimgs/img3.png "Image3")


 the `Constants.startwp_timer` defines how long the player has to wait at the
 first waiting page
 before he or she has an option to finish the game without waiting for
 others.

If a player chooses to finish the game his/her field `Player.outofthegame` is set to `True`, and all other pages are not shown to him.

The second task: informing players for how many other players they have to wait before they can proceed, is done using Channels.
