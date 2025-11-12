import {
  Box,
  Card,
  CardBody,
  Heading,
  IconButton,
  useClipboard,
  useToast,
  Text,
  Divider,
  VStack,
  HStack,
  Tooltip,
} from "@chakra-ui/react";
import { CopyIcon, DownloadIcon } from "@chakra-ui/icons";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { saveAs } from "file-saver";

const BlogResult = ({ content }) => {
  const { onCopy } = useClipboard(content);
  const toast = useToast();

  const handleCopy = () => {
    onCopy();
    toast({
      title: "Copied to clipboard",
      status: "success",
      duration: 2000,
      isClosable: true,
    });
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/markdown" });
    saveAs(blob, "generated-blog.md");
  };

  return (
    <Card bg="white" boxShadow="lg" borderRadius="xl" overflow="hidden" mt={6}>
      <CardBody p={0}>
        <Box p={6} borderBottomWidth="1px">
          <HStack justify="space-between" mb={4}>
            <Heading size="md" color="brand.700">
              Generated Blog
            </Heading>
            <HStack>
              <Tooltip label="Copy to clipboard">
                <IconButton
                  icon={<CopyIcon />}
                  onClick={handleCopy}
                  aria-label="Copy to clipboard"
                  colorScheme="brand"
                  variant="ghost"
                />
              </Tooltip>
              <Tooltip label="Download as Markdown">
                <IconButton
                  icon={<DownloadIcon />}
                  onClick={handleDownload}
                  aria-label="Download as Markdown"
                  colorScheme="brand"
                  variant="ghost"
                />
              </Tooltip>
            </HStack>
          </HStack>
          <Divider mb={4} />
          <Box
            className="markdown-content"
            p={4}
            borderRadius="md"
            bg="gray.50"
            overflowX="auto"
          >
            <ReactMarkdown
              components={{
                h1: ({ node, ...props }) => (
                  <Heading as="h1" size="xl" color="brand.700" my={4} {...props} />
                ),
                h2: ({ node, ...props }) => (
                  <Heading as="h2" size="lg" color="brand.600" my={3} {...props} />
                ),
                h3: ({ node, ...props }) => (
                  <Heading as="h3" size="md" color="brand.500" my={2} {...props} />
                ),
                p: ({ node, ...props }) => <Text my={4} lineHeight="tall" {...props} />,
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
                a: ({ node, ...props }) => (
                  <a
                    style={{ color: '#4f46e5', textDecoration: 'underline' }}
                    target="_blank"
                    rel="noopener noreferrer"
                    {...props}
                  />
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </Box>
        </Box>
      </CardBody>
    </Card>
  );
};

export default BlogResult;
