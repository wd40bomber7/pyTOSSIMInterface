Ñò
èPc        	   @   s   d  Z  d d k Z d d k Z d d k Z d d k Z d d k Z d d k l Z d e i f d     YZ	 d e i
 f d     YZ d S(   s/   
Created on Oct 12, 2012

@author: wd40bomber7
iÿÿÿÿN(   t   MessageTypet   ConfigWindowc           B   s§   e  Z d  Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z	 d   Z
 d	   Z d
   Z d   Z d   Z d   Z d   Z d   Z d   Z d   Z RS(   s6   
    A MDI child class made for displaying output
    c         C   su  t  t |   i | d  t i   |  _ |  i |  i  |  i i |  i d  |  i	   t i
 t i  } t i
 t i  } t i |  t i d  } | i | d t i d  t i |  t i  |  _ |  i t i |  i |  i  | i |  i d  | i d d  t i |  t i d	  } |  i t i |  i |  | i | d t i  | i | d t i t i Bt i Bt i Bd  | i d d  t i
 t i  } t i |  t i d
  } | i | d t i d  t i |  t i  |  _ |  i t i |  i |  i  | i |  i d  | i d d  t i |  t i d	  } |  i t i |  i  |  | i | d t i  | i | d t i t i Bt i Bt i Bd  | i d d  t i
 t i  } t i |  t i d  } | i | d t i d  t i |  t i  |  _! |  i t i |  i" |  i!  | i |  i! d  | i d d  t i |  t i d	  } |  i t i |  i# |  | i | d t i  | i | d t i t i Bt i Bt i Bd  | i d d  t i
 t i  } t i |  t i d  } | i | d t i d  t i |  t i d t$   |  _% |  i t i |  i& |  i%  | i |  i% d  | i | d t i t i Bt i Bt i Bd  | i d d  t i |  t i d  } | i | d t i' d  t i( |  t i  |  _) | i |  i) d t i t i Bt i Bt i Bt i* Bd  t i
 t i  } t i+ |  t i d  |  _, |  i t i- |  i. |  i,  | i |  i, d t i d  t i |  t i d  } |  i t i |  i/ |  | i | d t i' d  t i |  t i d  } |  i t i |  i0 |  | i | d t i d  | i | d t i t i Bt i Bt i Bd  | i d d  |  i1   |  i2 |  |  i3   d S(   s   
        Constructor
        s   Config Windowt   Presetss   Python File: i    i   i   i
   iÿÿÿÿt   Browses   Topo File: s   Noise File: s   Opcount per second: t	   validators   List of All Valid Channelsi   s   Autolearn New Channelss   Add Channels   Delete ChannelN(4   t   superR   t   __init__t   wxt   Menut
   presetMenut   RegisterMenut   menuBart   Appendt   RebuildMenust   BoxSizert   VERTICALt
   HORIZONTALt
   StaticTextt   ID_ANYt   Addt   RIGHTt   TextCtrlt   pythonChildTextboxt   Bindt   EVT_TEXTt"   _ConfigWindow__OnPythonChildChanget	   AddSpacert   Buttont
   EVT_BUTTONt   _ConfigWindow__OnPythonBrowset   AddSizert   EXPANDt   LEFTt   TOPt   topoFileTextboxt   _ConfigWindow__OnTopoFileChanget   _ConfigWindow__OnTopoBrowset   noiseFileTextboxt    _ConfigWindow__OnNoiseFileChanget   _ConfigWindow__OnNoiseBrowset   NumericObjectValidatort   opCountTextboxt   _ConfigWindow__OnOpCountChanget   CENTERt   ListBoxt   channelListBoxt   BOTTOMt   CheckBoxt   autoLearnCheckboxt   EVT_CHECKBOXt'   _ConfigWindow__OnAutoChannelLearnChanget   _ConfigWindow__OnChannelAddt   _ConfigWindow__OnChannelRemovet   UpdateDisplayt   SetSizert   Show(   t   selft   simt	   baseVSizet	   nameHSizet   labelt   buttont   opcountHSize(    (    s2   /home/fire/Desktop/TOSSIMInterface/ConfigWindow.pyR      s    
...!.8.
c         C   s   |  i  i i |  i _ |  i  i i |  i _ |  i  i i |  i _ t	 |  i  i i
  |  i _ |  i  i i |  i _ |  i i |  i  i i  d  S(   N(   R9   t   selectedOptionst   childPythonNameR   t   Valuet   noiseFileNameR%   t   topoFileNameR"   t   strt   opsPerSecondR)   t   autolearnChannelsR0   R