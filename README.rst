grepmx
=======

Grep lines in a file where email matches a given MX.

Installation
-----

.. code-block:: bash

    pip install grepmx


Usage
-----

Lets say you have a CSV file with user information, e.g.

.. code-block::

    firstname,surname,email,city
    Michelle,Shelly,michelleshelly@yahoo.com,Kearny
    Daniel,Boone,danielboone@gmail.com,New York
    Michael,Fletcher,michaelfletcher@yahoo.co.jp,St Anne
    Maria,Sauer,mariasauer@rocketmail.com,Arlington
    Maryjane,Porter,maryjaneporter@aol.com,Southfield

and you want to find all lines with a yahoo MX, the command would be:

.. code-block:: bash

    grepmx -m .yahoodns.? -m .yahoo.co.jp users.csv

the output is then all but the gmail.

To explain a bit what goes on with `.yahoodns.?`:

* The starting dot means yahoodns and any subdomain e.g. mx-aol.mail.gm0.yahoodns.net. but not otheryahoodns.net
* The ending questionmark tries to match on TLD, e.g. yahoodns.org or yahoodns.net

Multiple patterns can be used by using multiple `-m` arguments.

License
-------

MIT, see LICENSE