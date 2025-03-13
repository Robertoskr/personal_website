# Celery vs Cloud Run vs Cloud Functions/lambdas vs AWS batch

Over the last few months, I've been testing different solutions for running background tasks and jobs in my applications. I'm writing this post to share my learnings and comparisons, hoping to help you choose the right solution and architecture for your use case. 

## The Application/Requirements

My use case is straightforward. A user visits my application and makes a query, for example: 
"Companies that have good reviews on their website and are AI-related" (we are building a search engine for companies). To achieve this, we do two things:

1. Generate N candidates for the user query.
2. For each company, we use AI agents to conduct additional research and verify they match the user requirements.

This process needs to run in the background for several reasons:

1. It takes about 2 minutes on average to process 100 companies.
2. It is CPU intensive (we are doing dynamic RAG for each company: https://arxiv.org/abs/2312.08976)
3. Multiple users may submit queries simultaneously, and we need to prevent server overload.

## Evolution of Our Processing Architecture

During our product and tech iteration, we explored various approaches to handle company processing. Let me walk you through our journey:

### AWS Batch - The First Try

Our initial solution leveraged AWS Batch, spinning up a new EC2 instance for each user query. While this provided perfect isolation between queries and allowed concurrent processing within each instance, we hit a major roadblock: the cold start times were averaging around 1 minute. For our use case, this was simply unacceptable.

### AWS Lambda - Almost There

Moving to AWS Lambda seemed like the natural evolution. The implementation worked smoothly until we discovered that new AWS accounts are limited to 10 concurrent Lambda executions. Adding to this, we were running low on AWS credits, and GCP was offering some attractive free credits. Time for a change!

### GCP Cloud Run with Celery - The Complex Solution

On GCP, I first tried implementing Celery services within Cloud Run. The setup maintained one instance constantly running, with Cloud Run handling auto-scaling based on CPU usage. While functional, it felt overly complex and more like a workaround - Cloud Run wasn't really designed for this use case. One advantage of Celery was that it's open source, avoiding vendor lock-in, but setting it up on a VM wasn't an option either, as it would mean paying for idle time and potential scaling issues during peak usage.

### Finding The Right Fit

After the Celery setup showed its limitations, I was torn between two options:

- Cloud Functions (GCP's Lambda equivalent)
- Cloud Run HTTP service dedicated to company processing

### The Winner: Cloud Run HTTP Services

I ultimately chose Cloud Run HTTP services for its simplicity in setup and testing. Here's how our current implementation looks:

```python
def _process_company_qa_steps(body: dict):
    def _send():
        requests.post(PROCESS_COMPANY_QA_STEPS_ENDPOINT, json=body)
    thread = Thread(target=_send)
    thread.start()
```

Then you can just define each task as an http endpoint. 

This straightforward approach just fires off an HTTP request and moves on - no waiting for results or complex management needed. The benefits are significant:

- Easy local testing
- Minimal maintenance overhead
- Built-in auto-scaling
- Cost-effective

The current setup is working great, and I'm quite happy with how it turned out. Sometimes the simplest solution really is the best one!

## Comparison of Background Processing Solutions

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| AWS Batch | • Perfect isolation<br>• Full EC2 capabilities<br>• Good for heavy processing | • Long cold start (~1min)<br>• Higher costs<br>• Complex setup | Long-running batch jobs requiring significant resources, and without the need for fast results. |
| AWS Lambda | • Fast cold start<br>• Pay per use<br>• Simple deployment | • Concurrent execution limits<br>• Max runtime limitations<br>• Vendor lock-in | Short-running tasks with variable load |
| Celery + Cloud Run | • Open source<br>• Flexible architecture<br>• Good scheduling features | • Complex setup<br>• Requires message broker<br>• Overhead maintenance | Complex job queuing with specific scheduling needs |
| Cloud Run HTTP | • Simple implementation<br>• Easy testing<br>• Auto-scaling<br>• Cost-effective<br>• Can define max concurrent requests per instance | • HTTP timeout limits<br>• Less sophisticated queuing<br>• Potential for request losses | Medium-complexity tasks needing good scalability and simple implementation |

### Decision Framework

- Choose **AWS Batch** if you need full VM capabilities and have long-running jobs (hours)
- Use **AWS Lambda/Cloud Functions** for short, burst workloads with varying concurrency
- Consider **Celery** when you need advanced job scheduling and want to avoid vendor lock-in
- Pick **Cloud Run HTTP** for a balance of simplicity, cost, and scalability with moderate processing needs

**Are you in the process of figuring this out for your application? Shoot me an email, I'm happy to chime in and try to help! roberto.kalinovskyy@gmail.com**
