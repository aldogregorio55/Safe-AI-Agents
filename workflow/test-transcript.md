# Test Transcript — Source to Pay Workshop

**Purpose:** Anonymized transcript for Sandbox Workflow 1 (Client Pain Point Analysis)
**Original date:** 10 June 2025
**Anonymized:** 2026-04-10

**Anonymization key (internal reference only — do not include in agent input):**
- Speakers renamed to **Grace** and **Rocky**
- Company name → **Meridian**
- Legacy ERP → **Prism** (originally a real ERP product)
- Expense/purchasing tool → **Nexus** (originally a real expense management product)
- Government care program → **NCP** (originally a real national program)
- Business unit code → **CS** (originally a real BU abbreviation)

---

## Transcript

10 June 2025, 06:37am

Rocky started transcription

Grace   0:04
Hey, process taxonomy today and ultimately what we want from you today is to to state your views and participate during the session.
Be future focused, but have you know critical context around current state and employee experience and think about opportunities to transform the way that finance services are delivered, including areas of standardisation, centralization and automation, and the intent of this workshop is then to jointly determine actionable Nets next steps and if I can ask that everyone avoids multitasking, um.
So the way we're gonna frame up today session is you know, it's intended to be, you know, an initial session before we go into deep dives on specific topics.
But if you can see on the screen here, we've got the source to pay process taxonomy.
So this is a a core area of finance and and the way to read this across level 1-2 and three is at the level one across the top, you'll see source to contract and then underneath that at a Level 2 and Level 3 goes into more detail out of scope for today's workshop is the level four and five which is the the role based process flows ohh for activities that are performed on system and and out of system.
So we are gonna keep it at this level today and then on the right hand side, what you'll see is process governance around you know, reporting analytics, managing the process and and and system governance.
And so in terms of kicking off, we're gonna go left to right.
So from a source to contract perspective, Rocky, what I'm interested to know just at a high level is some of the current state technology that's being used today and and whether that current state technology across source, the contract is consistent across the organisation or are there multiple tools in play?
So I'll start there just from a high level perspective on tech.

Rocky   2:18
Yeah, absolutely, Grace.
So let me share a high level perspective.
Our core ERP is Prism.
So that's where we manage a lot of the purchasing.
We also have Nexus as well and that's actually the place where people in the business will raise purchase orders.
And also manage expenses.
So that's where we have our expense management sitting with you know, corporate credit card spend and people looking for reimbursements.
And then lastly, when we think about the procure our procurement operations at Meridian, we don't have any strategic procurement solution.
So all of our supplier uh risk management sourcing activities, contract management is offline and then the other thing to note as well is that for our direct spend.
So this is the spend or the purchases that are made within each of the bus to deliver their services.
A lot of this relates to the pass through spend and will be managed by the operational systems within each of the bus.

Grace   3:46
Ohh so in terms of playing that back, if we think about cause we've spoken about a lot of the taxonomy here.
So if we think about the source, the contract aspect, which includes procurement strategy, strategic category management, supplier relationship management, strategic sourcing, contract life cycle management, is it a fair summary to say all of that is offline in current state with the supplier master data aspect maintained in in Prism for Meridian purchasing?

Rocky   4:23
The that's right.
And we actually do create a certain.
So yes, all of those upstream processes are effectively offline, but as far as supplier master data goes, again, there's a whole bunch of supply master data that we manage in the operational systems.
But when it comes to our indirect Corporate spend, we actually create those suppliers in Nexus and then there's a manual process which has a lot of challenges with keeping data reconciled and manual offline processes and potentially even some segregation of duties.
Challenges to then update those supply master data records in Prism as well, based on the Nexus data.

Grace   5:16
Yeah.
So is the plan Rocky from a future state perspective with the upstream operational systems, is the plan to bring purchasing activities and supplier master data into the core ERP as part of future state or is the plan Retain in upstream systems and integrate from a financial perspective into into core Ledger?

Rocky   5:48
Yeah, it's absolutely a pain point that we need to look at.
And it does depend on the operational process and the role that.
Procurement has in those operational processes.
So for example, I think one of our principles for the future ERP is that we will make all payments out of the ERP.
So therefore, where we're creating suppliers in upstream operational systems, we also need to reflect those suppliers in our core ERP as well with all of the relevant master data around payment terms and so on South that we can pay them from the IP based on payments data that we would receive from upstream.

Grace   6:40
Yeah.
So from a design patent perspective, initial thinking is OK to pay file coming from upstream operational systems where the supplier relationship is owned.

Rocky   6:51
Yes.

Grace   6:54
However, there needs to be a synchronisation of that supply master data between upstream operational systems and future state ERP.

Rocky   7:05
Yep, that sounds right.

Grace   7:08
Yeah.
And in terms of the on that topic, so from a?
Supply. Ohh.
Relationship perspective with those upstream operational systems.
Do suppliers have access to a self service portal or portals with those upstream operational systems where they can update things like payment terms?
Sorry, payment methods, course supply masturbator like, you know, address information, etcetera.
Is that available or is that a process that upstream?
Operational folks have to update on behalf of clients.

Rocky   7:52
Yeah.
Again, it really depends on the the be U.
If I imagine one of the BUS which is CS, that's where we have our NCP plan management business.
We can receive uh, you know, upwards of 16,000 supply invoices per month and in total we can have at anytime up to 70,000 different suppliers for that BU in in terms of operational direct spend.
So we actually have a process where we are capturing the supplier master data based on some of the supply information that we receive in the invoice headers and then running extra validations based on that.
So it does depend from an operational perspective.
It does depend on the nature of the UK operations, but certainly from a corporate perspective where we manage our indirect spend and have our indirect suppliers, we don't have any type of supplier portal and that's a big pain point today because it does Dr inquiry based demand into the AAP team.

Grace   9:08
Hmm.

Rocky   9:10
Hi Sir as an example you know someone in the business might get a question from a supplier which relates to Corporate spend that we have committed to.
And then that question needs to find its way back to AP so that they can then go into either Nexus or Prism.
Find the right answer and then via email or phone call get back to that person in the business so that they can then reply to the supplier.
So it's quite a manual non value adding process for us in the current state.

Grace   9:49
So so understanding that I'm gonna note down a couple of transformational opportunities that we wanna pursue.
Which one is on the indirect spend?
You know, leveraging core ERP functionality for supplier self service portal to drive, you know, automation for supply records and and Updates.
And then on the direct band where operational systems are involved from a supplier master data perspective, UM having that integrated with the ERP.
However, putting in the right, you know, controls and validations to make sure that supply record cannot be updated on the ERP side when the source of truth for that supply record is is in an upstream system.
So add those to the the parking lot for transformational opportunities.
In terms of requisitioning, so as we work through.
Meridian is direct and indirect.
Spend what's the current state around?
Sort of.
No PO, no pay policies and you know enforcement of of requisitions, because that will be important as we think about future state design around, you know, wrecks and automatic PO creation.
And you know invoicing and and three way match.

Rocky   11:17
Yes, Sir.
Absolutely.
So as far as requisitioning goes, when when we think about the direct, sorry, the indirect Corporate spend, we don't use requisitions today.
And one of the really big challenges we have with indirect Corporate spend is exactly what you mentioned in forcing a number PO no pay policy because more often than not our AP team is actually retrospectively creating PCOS in Nexus so that when we receive an invoice from suppliers, it can be processed effectively in Nexus.
So we really need, we really don't have a user friendly process to enable the business to raise a requisition or a process order.
Uh in advance so that we know what span we've committed to, which can then unlock that process downstream to match up the supply invoice when it gets sent to us by the supplier.

Grace   12:26
And is that an area on the indirect spend side that Meridian is open to cataloguing as a transformational opportunity to from a policy perspective?
You know frame the requirement for requisitions on interact spans and then make sure from a process perspective as well as a a training throughout the business perspective to to make sure people are adequately trained on, you know, the enforcement of that policy.

Rocky   12:51
Hmm.
Yeah, definitely.
I think 4 our operational business.
So for the direct spend, if I think about our CS SBUI don't think the concept of a requisition necessarily.

Grace   13:04
Hmm.

Rocky   13:12
Applies to that BU or would be relevant for their business.
The spend that goes through their side of the business is more triggered by the NCP plan that they've set U for a particular NCP recipient.
So there is not really the concept of needing to raise a requisition and get that approved to incur spend for Meridian, but I think making the purchasing experience easy for people who need to incur Corporate spend through a A A well controlled requisition process will be a big improvement for us.
And I would say we definitely need that will be a big change.
So we definitely need to think about the training, training and change that enables that because it could potentially impact quite a lot of people across our organisation.

Grace   14:10
Yeah. Yep.
And one thing that you know, based on you know, the workshop that we're having today, which is obviously at you know a macro level, one thing that will put sort of in the parking lot as an action item is based on the different design patterns for spend across direct and indirect who won A-frame up sort of current state design patterns including you know technology as as well as sort of processes and then be able to map it into a future state design pattern in terms of, you know requisition needing applicable not applicable you know system that.

Rocky   14:49
Hmm.

Grace   14:53
We're gonna operational system that we're gonna use and the the nature of integration with the Ledger for from a payment perspective.

Rocky   15:01
Yes.

Grace   15:01
So that's something we'll put in the parking lot, you know, quarter to document that at a level of detail to have that current future state view as well as call out some of the change impacts on that.

Rocky   15:12
Yeah, that would be great.
And I think one of the other big pain points we have in their current state is that duplication between the PO that needs to be raised in Nexus and then the poo that then needs to get reflected in Prism um based on the PO from Nexus.
So I think in an ideal state, when we think about our future EP, it would be great to move away from that purchasing process that's supported by Nexus and bring that more into the core ERP.
So that it makes it much more easier to bring together the purchasing the supply invoices and then the payment that goes out from our bank account.

Grace   15:56
Yep.
And then from a Nexus perspective as a part of this programme, I should know the answer to this.
But is that a non strategic platform that you know one of the objectives is to move away from?
Source to pay processing on on the Nexus.

Rocky   16:15
I think I think we would like to move our procurement processes that are supported by Nexus today back into the Corey IP.
But expense management works OK and it's less of a priority for us.
So I think it again, it probably depends on what EP we select, but it's something that we can keep in Nexus for the time being and potentially consolidate onto one platform down the track depending on what ERP we select.

Grace   16:50
And understood.
And then and then from a source to contract perspective in terms of you know the offline processes that are currently in place today, is there a a future state vision to uplift that to be a tech enabled solution on preferred vendor ERP vendor?

Rocky   17:14
Yes.
Yeah, I think so as well.
But again, it's the same.
It's the same challenge, so in terms of our overarching business, Corporate spend is not a is not a huge part of our business.
And as much as our procurement laid would love to have a strategic sourcing solution to manage the Corporate spend contracts, it's probably not a horizon one priority for us, but we still should evaluate how the AIP vendors can solve this problem for us down the track because we do have a number of pain points in terms of managing our. Ohh.
Supplier contracts for Corporate spend understanding, you know, are we spending on contract?
What's our off contract spend?
Are we getting the best price for the goods and services that we buy on a routine basis and all of those other really key insights that will enable us to drive procurement savings?

Grace   18:26
Understood.
So I procurement obviously there's opportunity to uplift, but not a priority one or a phase one in in terms of you know uplifting that capability in terms of.
You know, reporting and month end.
What are some of the core pain points you know across the finance team that are seen around, you know, closing and and reconciling subledgers with the general Ledger, performing reconciliations, including sort of some of the daily, you know, bank reconciliations and matching and and and more broadly reporting?

Rocky   19:08
Yeah.
So there are a lot of challenges and pain points at month end.
I think #1 the challenges we have around the bank reconciliations.
There were a lot of manual steps to bring in the bank statement and reconcile that against payments that have been made. There's.
Some.
There is some.
There is some pots of our service delivery model that are not optimised.
So for example, some finance teams in the BU will perform part of the process and perform part of even payment processing.
Uh as it relates to Corporate spend and then even within our shared services team, you will see that the AP team is performing part of the process for payments to suppliers and the bank statement reconciliation that goes with that.
But they also do other processes as well that you might not expect them to do.
So I think we have a really big opportunity to optimise our processes at month end and really optimise which teams are performing which part of the process.
And then on reporting, I think a lot of our reporting is very manual in the current state and we have to download a lot of extracts from Prism and then manipulate those in spreadsheets offline to get the to get the insights we need to make decisions.
So there's a big opportunity there for us to rethink how we would use an AI P to drive more effective and efficient reporting.

Grace   21:06
So a couple of things based on some of those current state pain points, you know there's a great opportunity for us given the different stakeholders that are involved in you know the end to end process that we're looking at to do sort of a current state to future state service delivery model mapping.
Um, so we'll leverage sort of our tax enemies here again in the parking lot to sort of map out where current state teams are playing a role and then bring in sort of our future state perspectives on you know what good looks like for finance to a future state mapping.
Ohh secondly, the point on reporting obviously Prism in the legacy system, it sounds like there's a lot of extracts and putting together a lot lot of cost of production activities.
So cross, you know, if you just stay core ERP, there's a lot of delivered reporting to take advantage of and then you know from a um dashboarding perspective and an analytics perspective, you know there's really good starting point baseline there.
So one of the things we'll do in a a parking lot is make sure we we capture the reporting inventory that you've currently got.
So we can do an assessment in terms of, you know, fit gap to of from to a future state perspective just on the the reconciliation in terms of you know payments going out um and performing the bank Recs like what A at a high level, some of the main causes of of breaks there is it because a lot of the detail is sitting within you know upstream operational systems or is it you know a bank reconciliation file we haven't looked at that for many, many years and there's an opportunity to uplift that file that we're getting.
From the bank, do you have anymore insights in terms of what are some of the drivers of of reconciliation challenges?

Rocky   23:10
Yeah, I think #1 challenge is getting a more integrated A in is driving more integration with our bank.
So I think we have manual processes today to get the bank statement and then upload that into our EP, which takes time and effort and has risks associated with it.
So we'd be looking for a much more integrated host to host solution with our banking partner.
And then, because of the nature of our business, we have a lot of.
Reconciliation and clearing account challenges.
Particularly because a lot of our BUS really operate as a pass through clearing House.
So not only do we need to keep our bank reconciled, we also need to keep the clearing accounts reconciled as well.
So making sure that the outgoing payments that we made to suppliers a matched off against the incoming receipts from the various our customers or third parties that would be Funding those and there can be a whole bunch of business reasons why there might be reconciliation outages in those clearing accounts ranging from timing issues.
Uh, right through to the typical many to one matching issues that you might expect ranging right through to unidentified payments that HMM or or unmatched payments that require our team to trace back through transactional histories and understand extra descriptions or references which might give clues as to why particular payment or receipt is not clearing off against something else.

Grace   25:18
And have you got in current state to support with whether it be reconciliation, workflow or tracking of the clearing accounts?
Have you got a current state reconciliation tool that you're using?

Rocky   25:33
It's all excel.
No, we don't have any reconciliation tool, but I think this would be a great opportunity for us in the future because our teams are currently managing very complicated Excel worksheet excel workbooks where they need to extract source files from systems.
Run macros categorise data.
O2 data cleansing and then track reconciling items in manual offline processes which doesn't give us the control and visibility that we need to make sure that the clearing accounts are appropriately cleared from a financial control perspective.

Grace   26:23
Perfect.
So that that'll be an important consideration around future state ERP around the two aspects of reconciliations, the sort of payment for our bank reconciliations and then also the clearing account activity that you've got cause you know ERP vendors, you know do do things slightly differently and that consideration around you know best of breed tool to potentially support the Meridian end to end reconciliation requirements will be important.
And then from a like stepping back cross you know source the contract requisition to pay, you know, Meridian's definition of direct and indirect.
Um, any broader, you know, opportunities based on pain points around, you know, centralization, standardisation, you know automation based on sort of pain points race today.

Rocky   27:23
I don't think Sir Grace, I think we've covered it off pretty comprehensively.
We do.
We are a small organisation so we don't have a big central procurement department, so it will be important for us to enable more of a decentralised procurement operating model while maintaining A level of central visibility and control over the procurement that happens across the organisation.

Grace   27:57
Perfect.
But in terms of summarising some some actions from today's session.
So today we've sort of introduced the source to pay process taxonomy and you know spoken about pain points and opportunities across that taxonomy.
A few things that we'll do post workshop in Deep Dive sessions with the relevant subject matter experts is we'll do an overlay of this taxonomy around current to future state technology.
So we've spoken about upstream operational systems.
We've spoken about Nexus.
We've spoken about Prism.
Ohh, so we'll use it from a technology layer perspective in terms of when we think about future state, what core technology and supporting technology will be in play that will create you know integration requirements will also do a service delivery model overlay as well.
So we've spoken about multiple teams involved in the end to end process today and the various handoffs.
So we'll look at current state mapping to sort of future state and where we want to get to from an aspirational perspective.
And then we'll also start to capture pain points.
So where where our core pain points across the taxonomy and then start to think about, you know, either ERP requirements in terms of the selection that we're about to go on or you know what are some of those transformational initiatives that we can develop over a you know short term medium term long term horizon.
Um, it's one more thing in my head and I've forgotten that.
And then and then because it is a complex area in terms of, you know, source to pay and the interaction with you know upstream operational and interact and direct what will work with you on is starting to map out, you know, all of the way in terms of you know invoicing today the various use cases and design patterns that exist today.
So then we can apply a future state lands to that in terms of supply, master data management and how do we keep you know future state systems In Sync, um as well as requisitioning automatic PO creation and invoicing where that's applicable and where that's not applicable as well as then on the expense side in terms of Nexus, what we've heard today is Nexus is the strategic solution at this point in time for expense management.
So how does that fit in with, you know, integration requirements with the Ledger?
So we'll share a list of sort of a discussion that we've had today, the meeting minutes as well as you know the the action items that I've just replayed.
Was there anything else from an action item perspective that we wanted to add to that, the deep dive list?

Rocky   30:53
No, I think you've summarised the next steps and actions very well, Grace.
So thank you for that.
And looking forward to getting stuck into those actions as we shape the future of source to pay.

Grace   31:07
Perfect.
Thank you.

Rocky   31:09
Alright, thank you.

Rocky stopped transcription
