# clnrest - An [LNbits](https://github.com/lnbits/lnbits) Extension

<small>For more about LNBits extension check [this tutorial](https://github.com/lnbits/lnbits/wiki/LNbits-Extensions)</small>

<h2>*connect to your lnbits wallet using the CLN REST interface*</h2>

The clnrest extension for LNbits allows to make a connection to an LNbits wallet using a CLN REST interface, to perform Bolt11 and Bolt12 ([Bolt12 support for LNbits](https://github.com/lnbits/lnbits/pull/3663)) transactions, as well as to manage Bolt12 offers.
It is particularly useful with [Zeus](https://zeusln.com).
As it is meant to provide isolation from the underlying backend node through LNbits, node management functionalities are synthetic.
It does not strictly require an underlying CoreLightning backend (but Bolt12 support in LNbits is currently limited to CLN).

You add and enable the LNDhub extension on your left panel through the "Extensions" menue and scan the QR code that fits your needs.
With the "Invoice QR" you can give access to generating invoices and (only) receive sats into your wallet (e.g. useful for your waiters if you own a cafe).
With the "Admin QR" you also grant access sending / withdrawing from that wallet.
A reverse proxy can be used to remap the CLN REST URL, if needed.
