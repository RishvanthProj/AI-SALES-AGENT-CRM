# Automated Chatbot Failure Analysis & Root Cause Report
**System**: Starboyz AI Sales Agent & CRM  
**Date**: 2026-09-16 14:54:34 UTC  
**Total Failures**: 116 / 200 Single-Turn Tests (42.0% Pass Rate)  

---

## 1. Severity Distribution

| Severity Level | Count | Impact |
|---|---|---|
| **CRITICAL** | **0** | System crashes, incorrect routing, state loss, price hallucinations |
| **HIGH** | **0** | Major intent detection failure, emoji policy breach |
| **MEDIUM** | **116** | Minor intent classification divergence or ambiguous query grouping |
| **LOW** | **0** | Minor formatting nuances |

---

## 2. Failure Analysis & Root Cause Breakdown

### Failure 1: TC-GOOD-007 (Basic product enquiries)
- **Input**: `"What colors are available?"`
- **Expected**: Detect intent in ['product_enquiry', 'variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: Hey! It depends on which model you are looking at. Are you interested in our run...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['product_enquiry', 'variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-007`

---
### Failure 2: TC-GOOD-009 (Basic product enquiries)
- **Input**: `"Is there a smaller size available?"`
- **Expected**: Detect intent in ['product_enquiry', 'variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: Which model are you looking at, and what size do you need? Let me know the speci...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['product_enquiry', 'variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-009`

---
### Failure 3: TC-GOOD-012 (Basic product enquiries)
- **Input**: `"How much does the product weigh?"`
- **Expected**: Detect intent in ['product_enquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: pricing, Score: 30.0, Stage: route, Reply: Hey, all our shoes currently in stock, including the StrideAir Zoom, StrideGlide...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'pricing' expected '['product_enquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-012`

---
### Failure 4: TC-GOOD-013 (Basic product enquiries)
- **Input**: `"Is this suitable for daily use?"`
- **Expected**: Detect intent in ['product_enquiry', 'use_case'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey! That depends on what you have in mind for your daily routine. Are you looki...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['product_enquiry', 'use_case']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-013`

---
### Failure 5: TC-GOOD-018 (Basic product enquiries)
- **Input**: `"Can I see the available variants?"`
- **Expected**: Detect intent in ['product_enquiry', 'variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['product_enquiry', 'variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-018`

---
### Failure 6: TC-GOOD-020 (Basic product enquiries)
- **Input**: `"When will this product be back in stock?"`
- **Expected**: Detect intent in ['stock_check', 'restock'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['stock_check', 'restock']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-020`

---
### Failure 7: TC-GOOD-023 (Price-related enquiries)
- **Input**: `"Are there any additional charges?"`
- **Expected**: Detect intent in ['pricing', 'charges'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['pricing', 'charges']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-023`

---
### Failure 8: TC-GOOD-024 (Price-related enquiries)
- **Input**: `"Is shipping included in the price?"`
- **Expected**: Detect intent in ['pricing', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['pricing', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-024`

---
### Failure 9: TC-GOOD-034 (Price-related enquiries)
- **Input**: `"What payment options do you accept?"`
- **Expected**: Detect intent in ['payment_inquiry', 'general_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['payment_inquiry', 'general_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-034`

---
### Failure 10: TC-GOOD-035 (Price-related enquiries)
- **Input**: `"Can I pay online?"`
- **Expected**: Detect intent in ['payment_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['payment_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-035`

---
### Failure 11: TC-GOOD-036 (Price-related enquiries)
- **Input**: `"Is cash on delivery available?"`
- **Expected**: Detect intent in ['payment_inquiry', 'cod_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: Yes! Cash on Delivery is available across all serviceable pincodes in India, alo...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['payment_inquiry', 'cod_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-036`

---
### Failure 12: TC-GOOD-037 (Price-related enquiries)
- **Input**: `"Do you accept UPI payments?"`
- **Expected**: Detect intent in ['payment_inquiry', 'upi_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['payment_inquiry', 'upi_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-037`

---
### Failure 13: TC-GOOD-038 (Price-related enquiries)
- **Input**: `"Can I pay after receiving the product?"`
- **Expected**: Detect intent in ['payment_inquiry', 'cod_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['payment_inquiry', 'cod_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-038`

---
### Failure 14: TC-GOOD-039 (Price-related enquiries)
- **Input**: `"Are there any hidden charges?"`
- **Expected**: Detect intent in ['pricing', 'general_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['pricing', 'general_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-039`

---
### Failure 15: TC-GOOD-040 (Price-related enquiries)
- **Input**: `"Can you tell me the total amount before I order?"`
- **Expected**: Detect intent in ['pricing', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['pricing', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-040`

---
### Failure 16: TC-GOOD-042 (Variant and customization)
- **Input**: `"Can I choose a specific design?"`
- **Expected**: Detect intent in ['variant_query', 'customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['variant_query', 'customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-042`

---
### Failure 17: TC-GOOD-044 (Variant and customization)
- **Input**: `"Can you add a name to it?"`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-044`

---
### Failure 18: TC-GOOD-047 (Variant and customization)
- **Input**: `"Do you make personalized versions?"`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-047`

---
### Failure 19: TC-GOOD-048 (Variant and customization)
- **Input**: `"Can you make this according to my preference?"`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-048`

---
### Failure 20: TC-GOOD-049 (Variant and customization)
- **Input**: `"Can I send you a reference design?"`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-049`

---
### Failure 21: TC-GOOD-051 (Variant and customization)
- **Input**: `"How long does customization take?"`
- **Expected**: Detect intent in ['timeline_query', 'customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['timeline_query', 'customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-051`

---
### Failure 22: TC-GOOD-052 (Variant and customization)
- **Input**: `"Can I get a customized version for a birthday?"`
- **Expected**: Detect intent in ['customization_query', 'gifting'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query', 'gifting']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-052`

---
### Failure 23: TC-GOOD-053 (Variant and customization)
- **Input**: `"Can you add a short message to the product?"`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-053`

---
### Failure 24: TC-GOOD-054 (Variant and customization)
- **Input**: `"Can I order a custom quantity?"`
- **Expected**: Detect intent in ['bulk_query', 'customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['bulk_query', 'customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-054`

---
### Failure 25: TC-GOOD-055 (Variant and customization)
- **Input**: `"Can you make this in a different shape?"`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-055`

---
### Failure 26: TC-GOOD-056 (Variant and customization)
- **Input**: `"Can I choose the packaging?"`
- **Expected**: Detect intent in ['packaging', 'customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['packaging', 'customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-056`

---
### Failure 27: TC-GOOD-057 (Variant and customization)
- **Input**: `"Can you make a personalized gift set?"`
- **Expected**: Detect intent in ['customization_query', 'gifting'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query', 'gifting']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-057`

---
### Failure 28: TC-GOOD-060 (Variant and customization)
- **Input**: `"Can I change the design after placing the order?"`
- **Expected**: Detect intent in ['order_modification', 'policy_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['order_modification', 'policy_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-060`

---
### Failure 29: TC-GOOD-061 (Delivery and order enquiries)
- **Input**: `"How long will delivery take?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-061`

---
### Failure 30: TC-GOOD-062 (Delivery and order enquiries)
- **Input**: `"Do you deliver to Chennai?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'location_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'location_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-062`

---
### Failure 31: TC-GOOD-063 (Delivery and order enquiries)
- **Input**: `"Do you deliver across Tamil Nadu?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'location_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'location_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-063`

---
### Failure 32: TC-GOOD-064 (Delivery and order enquiries)
- **Input**: `"Do you ship throughout India?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'location_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['shipping_inquiry', 'location_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-064`

---
### Failure 33: TC-GOOD-066 (Delivery and order enquiries)
- **Input**: `"Can I get this delivered by Saturday?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-066`

---
### Failure 34: TC-GOOD-067 (Delivery and order enquiries)
- **Input**: `"I need this for a birthday next week. Is that possible?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 60.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-067`

---
### Failure 35: TC-GOOD-068 (Delivery and order enquiries)
- **Input**: `"How many days does dispatch usually take?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-068`

---
### Failure 36: TC-GOOD-069 (Delivery and order enquiries)
- **Input**: `"Do you provide tracking information?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'tracking_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'tracking_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-069`

---
### Failure 37: TC-GOOD-070 (Delivery and order enquiries)
- **Input**: `"How can I track my order?"`
- **Expected**: Detect intent in ['tracking_query', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['tracking_query', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-070`

---
### Failure 38: TC-GOOD-071 (Delivery and order enquiries)
- **Input**: `"Can I choose the delivery date?"`
- **Expected**: Detect intent in ['shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-071`

---
### Failure 39: TC-GOOD-072 (Delivery and order enquiries)
- **Input**: `"Can you arrange urgent delivery?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'urgent_delivery'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 60.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'urgent_delivery']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-072`

---
### Failure 40: TC-GOOD-073 (Delivery and order enquiries)
- **Input**: `"Is same-day delivery available in Chennai?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'location_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['shipping_inquiry', 'location_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-073`

---
### Failure 41: TC-GOOD-074 (Delivery and order enquiries)
- **Input**: `"How long does shipping usually take to Bangalore?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'location_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'location_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-074`

---
### Failure 42: TC-GOOD-075 (Delivery and order enquiries)
- **Input**: `"Can I change the delivery address after ordering?"`
- **Expected**: Detect intent in ['order_modification', 'policy_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['order_modification', 'policy_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-075`

---
### Failure 43: TC-GOOD-076 (Delivery and order enquiries)
- **Input**: `"Can someone else receive the package for me?"`
- **Expected**: Detect intent in ['shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-076`

---
### Failure 44: TC-GOOD-077 (Delivery and order enquiries)
- **Input**: `"Do you deliver on Sundays?"`
- **Expected**: Detect intent in ['shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Kandiga bro! StrideAir Zoom Casual Sneaker Rs. 1,499 ki available ga undi. Daily...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-077`

---
### Failure 45: TC-GOOD-078 (Delivery and order enquiries)
- **Input**: `"Will the package be safely packed?"`
- **Expected**: Detect intent in ['packaging', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['packaging', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-078`

---
### Failure 46: TC-GOOD-079 (Delivery and order enquiries)
- **Input**: `"Is gift wrapping available?"`
- **Expected**: Detect intent in ['packaging', 'gifting'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['packaging', 'gifting']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-079`

---
### Failure 47: TC-GOOD-080 (Delivery and order enquiries)
- **Input**: `"Can you send the order directly to the recipient?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'gifting'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'gifting']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-080`

---
### Failure 48: TC-GOOD-081 (Purchase-intent enquiries)
- **Input**: `"I would like to order one. What should I do?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-081`

---
### Failure 49: TC-GOOD-082 (Purchase-intent enquiries)
- **Input**: `"I want to buy this. Can you guide me through the process?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Great choice. Let's get your order placed for StrideAir Zoom Casual Sneaker (UK ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-082`

---
### Failure 50: TC-GOOD-083 (Purchase-intent enquiries)
- **Input**: `"How do I place an order?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Order Summary:
-----------------------------------------
Item:        StrideAir ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-083`

---
### Failure 51: TC-GOOD-084 (Purchase-intent enquiries)
- **Input**: `"Can you help me order this product?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-084`

---
### Failure 52: TC-GOOD-085 (Purchase-intent enquiries)
- **Input**: `"I need two of these. How can I purchase them?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-085`

---
### Failure 53: TC-GOOD-086 (Purchase-intent enquiries)
- **Input**: `"I'd like to buy this in pink."`
- **Expected**: Detect intent in ['purchase_intent', 'variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-086`

---
### Failure 54: TC-GOOD-087 (Purchase-intent enquiries)
- **Input**: `"I want 5 pieces for an event. Can you help me?"`
- **Expected**: Detect intent in ['purchase_intent', 'bulk_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'bulk_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-087`

---
### Failure 55: TC-GOOD-088 (Purchase-intent enquiries)
- **Input**: `"I want to place a bulk order. Whom should I contact?"`
- **Expected**: Detect intent in ['bulk_query', 'purchase_intent'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['bulk_query', 'purchase_intent']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-088`

---
### Failure 56: TC-GOOD-089 (Purchase-intent enquiries)
- **Input**: `"I'm ready to order. What details do you need?"`
- **Expected**: Detect intent in ['purchase_intent', 'checkout_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'checkout_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-089`

---
### Failure 57: TC-GOOD-090 (Purchase-intent enquiries)
- **Input**: `"Can you reserve one for me?"`
- **Expected**: Detect intent in ['reservation_query', 'purchase_intent'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['reservation_query', 'purchase_intent']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-090`

---
### Failure 58: TC-GOOD-091 (Purchase-intent enquiries)
- **Input**: `"Is there anything I need to know before ordering?"`
- **Expected**: Detect intent in ['general_query', 'policy_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['general_query', 'policy_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-091`

---
### Failure 59: TC-GOOD-092 (Purchase-intent enquiries)
- **Input**: `"Can you confirm whether I can order this today?"`
- **Expected**: Detect intent in ['purchase_intent', 'stock_check'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 60.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'stock_check']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-092`

---
### Failure 60: TC-GOOD-096 (Purchase-intent enquiries)
- **Input**: `"I need 20 pieces for a college event. Is bulk ordering possible?"`
- **Expected**: Detect intent in ['bulk_query', 'purchase_intent'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Please scan the QR code above to pay Rs. 1,499 using any UPI app. Once done, typ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['bulk_query', 'purchase_intent']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-096`

---
### Failure 61: TC-GOOD-097 (Purchase-intent enquiries)
- **Input**: `"I'm buying this as a birthday gift. What packaging options do you have?"`
- **Expected**: Detect intent in ['packaging', 'gifting'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['packaging', 'gifting']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-097`

---
### Failure 62: TC-GOOD-098 (Purchase-intent enquiries)
- **Input**: `"I like this product. Can you tell me the next step to purchase it?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-098`

---
### Failure 63: TC-GOOD-099 (Purchase-intent enquiries)
- **Input**: `"I'd like to place an order after confirming the delivery time."`
- **Expected**: Detect intent in ['purchase_intent', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-099`

---
### Failure 64: TC-GOOD-100 (Purchase-intent enquiries)
- **Input**: `"This looks good. Please tell me how I can order it."`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Your order has been confirmed!

-----------------------------------------
Order ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-GOOD-100`

---
### Failure 65: TC-DIFF-006 (Extremely short / incomplete)
- **Input**: `"delivery"`
- **Expected**: Detect intent in ['shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey! Are you asking about the delivery time for a new order, or do you have an e...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-006`

---
### Failure 66: TC-DIFF-007 (Extremely short / incomplete)
- **Input**: `"want this"`
- **Expected**: Detect intent in ['purchase_intent', 'product_enquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey! I am happy to help you out with that, but I am not sure which pair you are ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['purchase_intent', 'product_enquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-007`

---
### Failure 67: TC-DIFF-008 (Extremely short / incomplete)
- **Input**: `"buy"`
- **Expected**: Detect intent in ['purchase_intent'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Great choice. Let's get your order placed for StrideAir Zoom Casual Sneaker (UK ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-008`

---
### Failure 68: TC-DIFF-009 (Extremely short / incomplete)
- **Input**: `"order?"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Order Summary:
-----------------------------------------
Item:        StrideAir ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-009`

---
### Failure 69: TC-DIFF-012 (Extremely short / incomplete)
- **Input**: `"COD?"`
- **Expected**: Detect intent in ['payment_inquiry', 'cod_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Your order has been confirmed!

-----------------------------------------
Order ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['payment_inquiry', 'cod_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-012`

---
### Failure 70: TC-DIFF-013 (Extremely short / incomplete)
- **Input**: `"where"`
- **Expected**: Detect intent in ['location_query', 'general_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey! Are you looking for our store location? We are located at Starboyz Flagship...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['location_query', 'general_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-013`

---
### Failure 71: TC-DIFF-015 (Extremely short / incomplete)
- **Input**: `"how"`
- **Expected**: Detect intent in ['general_query', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey! How can I help you out today? Are you looking for some new shoes for runnin...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['general_query', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-015`

---
### Failure 72: TC-DIFF-019 (Extremely short / incomplete)
- **Input**: `"this?"`
- **Expected**: Detect intent in ['product_enquiry', 'general_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey! You just sent "this" but I do not see an image or a link attached to your m...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['product_enquiry', 'general_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-019`

---
### Failure 73: TC-DIFF-020 (Extremely short / incomplete)
- **Input**: `"send"`
- **Expected**: Detect intent in ['general_query', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey! Looks like you might have hit send a bit too early. Were you looking to che...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['general_query', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-020`

---
### Failure 74: TC-DIFF-024 (Broken / unclear English)
- **Input**: `"can u tell delivery fast?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-024`

---
### Failure 75: TC-DIFF-026 (Broken / unclear English)
- **Input**: `"i need this one but which color available"`
- **Expected**: Detect intent in ['variant_query', 'stock_check'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['variant_query', 'stock_check']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-026`

---
### Failure 76: TC-DIFF-027 (Broken / unclear English)
- **Input**: `"this can deliver today yes?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 60.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-027`

---
### Failure 77: TC-DIFF-030 (Broken / unclear English)
- **Input**: `"how many days coming"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-030`

---
### Failure 78: TC-DIFF-032 (Broken / unclear English)
- **Input**: `"where your shop located and shipping also?"`
- **Expected**: Detect intent in ['location_query', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['location_query', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-032`

---
### Failure 79: TC-DIFF-034 (Broken / unclear English)
- **Input**: `"i want order but don't know how"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-034`

---
### Failure 80: TC-DIFF-035 (Broken / unclear English)
- **Input**: `"this is original or duplicate?"`
- **Expected**: Detect intent in ['product_enquiry', 'authenticity'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['product_enquiry', 'authenticity']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-035`

---
### Failure 81: TC-DIFF-036 (Broken / unclear English)
- **Input**: `"send pic all colors"`
- **Expected**: Detect intent in ['variant_query', 'media_request'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['variant_query', 'media_request']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-036`

---
### Failure 82: TC-DIFF-038 (Broken / unclear English)
- **Input**: `"this price including shipping no?"`
- **Expected**: Detect intent in ['pricing', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['pricing', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-038`

---
### Failure 83: TC-DIFF-040 (Broken / unclear English)
- **Input**: `"if order now when receive"`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-040`

---
### Failure 84: TC-DIFF-044 (Slang / casual texting)
- **Input**: `"akka COD iruka?"`
- **Expected**: Detect intent in ['payment_inquiry', 'cod_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: Your order has been confirmed!

-----------------------------------------
Order ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['payment_inquiry', 'cod_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-044`

---
### Failure 85: TC-DIFF-046 (Slang / casual texting)
- **Input**: `"bro fast delivery possible ah?"`
- **Expected**: Detect intent in ['shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-046`

---
### Failure 86: TC-DIFF-050 (Slang / casual texting)
- **Input**: `"akka same color venum"`
- **Expected**: Detect intent in ['variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Kandippa bro! Namma kitta StrideAir Zoom Casual Sneaker stock la iruku (2 pairs ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-050`

---
### Failure 87: TC-DIFF-052 (Slang / casual texting)
- **Input**: `"delivery enga enga?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'location_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Kandippa bro! Namma kitta StrideAir Zoom Casual Sneaker stock la iruku (2 pairs ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'location_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-052`

---
### Failure 88: TC-DIFF-053 (Slang / casual texting)
- **Input**: `"vera design iruka bro?"`
- **Expected**: Detect intent in ['variant_query', 'product_enquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: Kandippa bro! Namma kitta StrideAir Zoom Casual Sneaker stock la iruku (2 pairs ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['variant_query', 'product_enquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-053`

---
### Failure 89: TC-DIFF-054 (Slang / casual texting)
- **Input**: `"pls reply"`
- **Expected**: Detect intent in ['general_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['general_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-054`

---
### Failure 90: TC-DIFF-055 (Slang / casual texting)
- **Input**: `"bro one piece kudu"`
- **Expected**: Detect intent in ['purchase_intent'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-055`

---
### Failure 91: TC-DIFF-058 (Slang / casual texting)
- **Input**: `"idhu super ah iruku how order"`
- **Expected**: Detect intent in ['purchase_intent', 'order_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['purchase_intent', 'order_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-058`

---
### Failure 92: TC-DIFF-059 (Slang / casual texting)
- **Input**: `"akka urgent venum"`
- **Expected**: Detect intent in ['urgent_delivery', 'shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 60.0, Stage: route, Reply: Kandippa bro! Namma kitta StrideAir Zoom Casual Sneaker stock la iruku (2 pairs ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['urgent_delivery', 'shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-059`

---
### Failure 93: TC-DIFF-062 (Contradictory / ambiguous)
- **Input**: `"Give me the cheapest expensive option."`
- **Expected**: Detect intent in ['product_enquiry', 'pricing'], ground against Firestore catalog, no emojis
- **Actual**: Intent: request_discount, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'request_discount' expected '['product_enquiry', 'pricing']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-062`

---
### Failure 94: TC-DIFF-063 (Contradictory / ambiguous)
- **Input**: `"I need 1 or maybe 10, tell me both."`
- **Expected**: Detect intent in ['pricing', 'bulk_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['pricing', 'bulk_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-063`

---
### Failure 95: TC-DIFF-064 (Contradictory / ambiguous)
- **Input**: `"I want blue, but don't send blue."`
- **Expected**: Detect intent in ['variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-064`

---
### Failure 96: TC-DIFF-065 (Contradictory / ambiguous)
- **Input**: `"I need it today but I'm okay with next week."`
- **Expected**: Detect intent in ['shipping_inquiry', 'timeline_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 60.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'timeline_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-065`

---
### Failure 97: TC-DIFF-066 (Contradictory / ambiguous)
- **Input**: `"I want a customized product but I don't want customization."`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-066`

---
### Failure 98: TC-DIFF-068 (Contradictory / ambiguous)
- **Input**: `"I need something small but also large."`
- **Expected**: Detect intent in ['variant_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['variant_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-068`

---
### Failure 99: TC-DIFF-072 (Contradictory / ambiguous)
- **Input**: `"Can you give me every available option?"`
- **Expected**: Detect intent in ['product_enquiry', 'catalog_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: stock_check, Score: 30.0, Stage: route, Reply: Order Summary:
-----------------------------------------
Item:        StrideAir ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'stock_check' expected '['product_enquiry', 'catalog_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-072`

---
### Failure 100: TC-DIFF-073 (Contradictory / ambiguous)
- **Input**: `"I want a cheap one but it should be premium."`
- **Expected**: Detect intent in ['product_enquiry', 'pricing'], ground against Firestore catalog, no emojis
- **Actual**: Intent: request_discount, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'request_discount' expected '['product_enquiry', 'pricing']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-073`

---
### Failure 101: TC-DIFF-074 (Contradictory / ambiguous)
- **Input**: `"I need something for everyone."`
- **Expected**: Detect intent in ['product_enquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['product_enquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-074`

---
### Failure 102: TC-DIFF-077 (Contradictory / ambiguous)
- **Input**: `"I need delivery tomorrow, but I haven't given my address."`
- **Expected**: Detect intent in ['shipping_inquiry'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 60.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-077`

---
### Failure 103: TC-DIFF-079 (Contradictory / ambiguous)
- **Input**: `"I need a customized item but I'm not sure what customization."`
- **Expected**: Detect intent in ['customization_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['customization_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-079`

---
### Failure 104: TC-DIFF-083 (Price negotiation / pressure)
- **Input**: `"Nobody will pay this price."`
- **Expected**: Detect intent in ['objection_price', 'pricing'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Hey Customer, welcome to Starboyz! What kind of shoes are you looking for today?...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['objection_price', 'pricing']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-083`

---
### Failure 105: TC-DIFF-084 (Price negotiation / pressure)
- **Input**: `"Your competitor is selling cheaper."`
- **Expected**: Detect intent in ['objection_price', 'competitor_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: request_discount, Score: 30.0, Stage: route, Reply: The StrideAir Zoom Casual Sneaker is available for ₹1,299.00 with fast doorstep ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'request_discount' expected '['objection_price', 'competitor_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-084`

---
### Failure 106: TC-DIFF-085 (Price negotiation / pressure)
- **Input**: `"Can you give it for ₹100?"`
- **Expected**: Detect intent in ['request_discount', 'pricing'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 70.0, Stage: route, Reply: Your order has been confirmed!

-----------------------------------------
Order ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['request_discount', 'pricing']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-085`

---
### Failure 107: TC-DIFF-088 (Price negotiation / pressure)
- **Input**: `"I want 20 pieces at the price of one."`
- **Expected**: Detect intent in ['request_discount', 'bulk_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: pricing, Score: 30.0, Stage: route, Reply: Please scan the QR code above to pay Rs. 1,499 using any UPI app. Once done, typ...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'pricing' expected '['request_discount', 'bulk_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-088`

---
### Failure 108: TC-DIFF-090 (Price negotiation / pressure)
- **Input**: `"If you don't reduce the price I'm leaving."`
- **Expected**: Detect intent in ['objection_price', 'request_discount'], ground against Firestore catalog, no emojis
- **Actual**: Intent: pricing, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'pricing' expected '['objection_price', 'request_discount']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-090`

---
### Failure 109: TC-DIFF-091 (Price negotiation / pressure)
- **Input**: `"I'll buy everything if you give me wholesale price."`
- **Expected**: Detect intent in ['bulk_query', 'request_discount'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['bulk_query', 'request_discount']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-091`

---
### Failure 110: TC-DIFF-092 (Price negotiation / pressure)
- **Input**: `"Can you make it free for me?"`
- **Expected**: Detect intent in ['request_discount', 'unreasonable'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['request_discount', 'unreasonable']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-092`

---
### Failure 111: TC-DIFF-093 (Price negotiation / pressure)
- **Input**: `"Why is this so expensive?"`
- **Expected**: Detect intent in ['pricing', 'objection_price'], ground against Firestore catalog, no emojis
- **Actual**: Intent: greeting, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'greeting' expected '['pricing', 'objection_price']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-093`

---
### Failure 112: TC-DIFF-094 (Price negotiation / pressure)
- **Input**: `"Price is too high bro."`
- **Expected**: Detect intent in ['objection_price', 'pricing'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['objection_price', 'pricing']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-094`

---
### Failure 113: TC-DIFF-095 (Price negotiation / pressure)
- **Input**: `"I saw it cheaper somewhere else."`
- **Expected**: Detect intent in ['objection_price', 'competitor_query'], ground against Firestore catalog, no emojis
- **Actual**: Intent: request_discount, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'request_discount' expected '['objection_price', 'competitor_query']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-095`

---
### Failure 114: TC-DIFF-097 (Price negotiation / pressure)
- **Input**: `"What is your best deal?"`
- **Expected**: Detect intent in ['pricing', 'offers'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['pricing', 'offers']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-097`

---
### Failure 115: TC-DIFF-098 (Price negotiation / pressure)
- **Input**: `"Make the price less and I'll order immediately."`
- **Expected**: Detect intent in ['request_discount', 'purchase_intent'], ground against Firestore catalog, no emojis
- **Actual**: Intent: pricing, Score: 60.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'pricing' expected '['request_discount', 'purchase_intent']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-098`

---
### Failure 116: TC-DIFF-099 (Price negotiation / pressure)
- **Input**: `"Can you somehow reduce the shipping charge?"`
- **Expected**: Detect intent in ['shipping_inquiry', 'request_discount'], ground against Firestore catalog, no emojis
- **Actual**: Intent: product_enquiry, Score: 30.0, Stage: route, Reply: Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have tr...
- **Severity**: `MEDIUM`
- **Reason**: Intent mismatch: detected 'product_enquiry' expected '['shipping_inquiry', 'request_discount']'
- **Root Cause**: Ambiguity in single-word or highly compressed customer query.
- **Recommended Fix**: Add contextual fallback mapping for short queries.
- **Regression Test ID**: `REG-TC-DIFF-099`

---
## 3. Recommended Fixes & Continuous Improvement

1. **Short Query Intent Boosting**:
   - For single-word messages like `"colors"`, `"size?"`, ensure default routing prioritizes active product catalog exploration rather than generic help.
2. **Dynamic Slang Lexicon Expansion**:
   - Continue expanding Romanized Tamil (Tanglish) and Hindi (Hinglish) keyword dictionaries for niche localized slang.
3. **Automated CI/CD Integration**:
   - Run `python run_chatbot_evaluation.py` on every git commit before triggering production deployment to Meta WhatsApp Cloud API.
